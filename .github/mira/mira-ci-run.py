"""Run the pinned Mira CLI with one routing execution and fail-closed results."""
import asyncio
import importlib.metadata
import os
import json
import urllib.request
from mira.llm.provider import LLMProvider
from mira.core.engine import ReviewEngine
from mira.exceptions import LLMError

IDENTITY = os.environ['MIRA_EXECUTION']
ROUTER_URL = os.environ.get('MIRA_ROUTER_URL', 'http://127.0.0.1:8001').rstrip('/')
original_headers = LLMProvider._build_headers

def headers(self):
    if self.config.base_url.rstrip('/') != ROUTER_URL + '/v1':
        raise RuntimeError('Unauthorized endpoint in CI configuration')
    return {'Content-Type': 'application/json', 'x-mira-execution': IDENTITY}

async def guard():
    def status():
        req = urllib.request.Request(ROUTER_URL + '/status', headers={'x-mira-execution': IDENTITY})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.load(resp)
    state = await asyncio.to_thread(status)
    if state['failed']:
        # Pinned Mira LLMError uses a message key and keyword parameters.
        raise RuntimeError('Mira review incomplete: ' + state['reason'])

original_review = ReviewEngine._review_diff_internal
async def guarded_review(self, *args, **kwargs):
    result = await original_review(self, *args, **kwargs)
    await guard()
    return result

if __name__ == '__main__':
    LLMProvider._build_headers = headers
    ReviewEngine._review_diff_internal = guarded_review
    entry = next(e for e in importlib.metadata.distribution('mira-reviewer').entry_points if e.name == 'mira')
    entry.load()()
