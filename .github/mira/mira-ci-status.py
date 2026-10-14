"""Read routing status without inference; fail closed if router is unavailable."""
import json,os,sys,urllib.request
from pathlib import Path
try:
 req=urllib.request.Request('http://127.0.0.1:8001/status',headers={'x-mira-execution':os.environ['MIRA_EXECUTION']})
 with urllib.request.urlopen(req,timeout=10) as response: state=json.load(response)
except Exception:
 state={'failed':True,'reason':'router_status_unavailable','route':'unknown','recoveries':0,'calls':0}
Path(sys.argv[1]).write_text(json.dumps(state))
print(json.dumps(state))
