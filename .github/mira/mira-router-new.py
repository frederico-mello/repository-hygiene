"""Mira Go -> Ollama router. Recovery budget is per execution, not per model."""
import json
import os
import time
import threading
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib

# Go-only fail-closed mode (MIRA_GO_ONLY=1), used by the issue_comment path:
# quota/auth/transient failures must terminate instead of selecting Ollama,
# and the OLLAMA_API_KEY is never loaded or read in this mode.
def go_only():
    return os.environ.get('MIRA_GO_ONLY', '') == '1'

# Load only the authorized credentials. Never print their values.
_envfile = Path.home() / 'AppData/Local/hermes/.env'
def load_envfile(path):
    if not path.exists():
        return
    allowed = ('OPENCODE_GO_API_KEY',) if go_only() else ('OPENCODE_GO_API_KEY', 'OLLAMA_API_KEY')
    for line in path.read_text(encoding='utf-8').splitlines():
        name, sep, value = line.removeprefix('export ').partition('=')
        if sep and name.strip() in allowed:
            os.environ.setdefault(name.strip(), value.strip().strip('\"\''))
load_envfile(_envfile)
STATE_DIR = Path.home() / 'tools/mira-routing-state'

def save_state(identity, state):
    # parents=True: a fresh home has no 'tools/' yet, and the first go-only
    # request must not die with FileNotFoundError before forwarding.
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / (hashlib.sha256(identity.encode()).hexdigest() + '.json')
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(state.summary()), encoding='utf-8')
    tmp.replace(path)
MODEL = 'deepseek-v4.1-flash'
ROUTES = {
    'go': ('https://opencode.ai/zen/go/v1/chat/completions', 'OPENCODE_GO_API_KEY'),
    'ollama': ('https://ollama.com/v1/chat/completions', 'OLLAMA_API_KEY'),
}
STATES = {}
LOCK = threading.RLock()
LIMIT = 6

class State:
    def __init__(self):
        self.route = 'go'
        self.recoveries = 0
        self.calls = 0
        self.failed = False
        self.reason = ''
        self.lock = threading.RLock()
        self.per_route = {'go': 0, 'ollama': 0}
    def consume(self):
        if self.recoveries >= LIMIT:
            self.failed = True
            self.reason = 'recovery_budget_exhausted'
            return False
        self.recoveries += 1
        return True
    def summary(self):
        data = {k: getattr(self, k) for k in ('route', 'recoveries', 'calls', 'failed', 'reason')}
        data['calls_by_route'] = dict(self.per_route)
        return data

def state_for(identity):
    with LOCK:
        if identity not in STATES:
            state = State()
            path = STATE_DIR / (hashlib.sha256(identity.encode()).hexdigest() + '.json')
            if path.exists():
                data = json.loads(path.read_text(encoding='utf-8'))
                for key in state.summary():
                    setattr(state, key, data[key])
            STATES[identity] = state
        return STATES[identity]

def forward(route, identity, body):
    if go_only() and route != 'go':
        # Fail closed before any credential lookup: in go-only mode the
        # OLLAMA_API_KEY is never read and no request reaches Ollama Cloud.
        return 503, json.dumps({'error': {'message': 'go_only_route_disabled'}})
    url, env = ROUTES[route]
    key = os.environ.get(env)
    if not key:
        return 401, json.dumps({'error': {'message': 'Missing credential for ' + route}})
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}
    if route == 'go':
        headers['x-opencode-session'] = identity
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        # Do not log upstream response bodies or credentials.
        return exc.code, exc.read().decode()
    except (urllib.error.URLError, TimeoutError, OSError):
        return 503, json.dumps({'error': {'message': 'upstream_transport_failure'}})

def route_and_call(body, identity, send=forward, pause=time.sleep):
    if not identity or len(identity) > 200:
        return 400, json.dumps({'error': {'message': 'Missing/invalid x-mira-execution'}})
    if body.get('model') != MODEL:
        return 400, json.dumps({'error': {'message': 'Model not allowed by deployment'}})
    state = state_for(identity)
    with state.lock:
        if state.failed:
            return 503, json.dumps({'error': {'message': state.reason}})
        payload = dict(body)
        # The installed model can reject forced tool_choice. Use auto initially
        # so the client does not perform an unbudgeted compatibility retry.
        if 'tools' in payload:
            payload['tool_choice'] = 'auto'
        attempts = 0
        while True:
            state.calls += 1
            state.per_route[state.route] = state.per_route.get(state.route, 0) + 1
            save_state(identity, state)
            code, result = send(state.route, identity, payload)
            if code == 200:
                # A 200 whose message has neither tool calls nor content is a
                # malformed model response (e.g. reasoning-only). Treat it as
                # a budgeted recovery, not a success: without this, the client
                # aborts the whole review on one ill-formed response.
                try:
                    message = json.loads(result)['choices'][0]['message']
                except (ValueError, KeyError, IndexError, TypeError):
                    message = None
                tool_composed = bool(message and message.get('tool_calls'))
                has_content = bool(message and message.get('content'))
                # Only check when tools are actually requested; a plain JSON
                # completion legitimately carries content and no tool_calls.
                if 'tools' in payload and not (tool_composed or has_content):
                    print(json.dumps({'execution': identity, 'event': 'malformed_response',
                                      'route': state.route, **state.summary()}), flush=True)
                    if not state.consume():
                        state.failed = True
                        state.reason = 'malformed_response_persistent'
                        save_state(identity, state)
                        break
                    attempts += 1
                    pause(2)
                    continue
                return code, result
            # Quota/auth errors are never retried on that provider. Go-only
            # mode never selects ollama: it falls through to the terminal
            # failure below and fails closed.
            if state.route == 'go' and code in (401, 403, 429) and not go_only():
                if not state.consume():
                    break
                state.route = 'ollama'
                print(json.dumps({'execution': identity, 'event': 'fallback', **state.summary()}), flush=True)
                continue
            if code in (408, 425, 500, 502, 503, 504) and attempts == 0:
                if not state.consume():
                    break
                attempts += 1
                pause(2)
                continue
            # One transient retry on Go failed: try fallback once. No bounce back.
            # Go-only mode never selects ollama: it falls through to the
            # terminal failure below and fails closed.
            if state.route == 'go' and code in (408, 425, 500, 502, 503, 504) and not go_only():
                if not state.consume():
                    break
                state.route = 'ollama'
                continue
            state.failed = True
            state.reason = 'upstream_failure_' + str(code)
            save_state(identity, state)
            return code, result
        save_state(identity, state)
        return 503, json.dumps({'error': {'message': state.reason}})

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def respond(self, code, body):
        data = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path == '/health':
            self.respond(200, json.dumps({'status': 'ok', 'router': 'go-ollama-v1'}))
            return
        identity = self.headers.get('x-mira-execution', '')
        if self.path == '/status' and identity:
            state = state_for(identity)
            with state.lock:
                self.respond(200, json.dumps(state.summary()))
            return
        self.respond(404, '{}')
    def do_POST(self):
        if self.path != '/v1/chat/completions':
            self.respond(404, '{}')
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 8000000:
                self.respond(413, '{}')
                return
            body = json.loads(self.rfile.read(size))
            code, data = route_and_call(body, self.headers.get('x-mira-execution', ''))
            self.respond(code, data)
        except (ValueError, TypeError):
            self.respond(400, '{}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
