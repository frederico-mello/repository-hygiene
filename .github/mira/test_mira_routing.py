import importlib.util,unittest,tempfile,pathlib,json,os
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('router',pathlib.Path(__file__).with_name('mira-router-new.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RoutingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent)
  r.STATE_DIR=pathlib.Path(self.tmp.name);r.STATES.clear();self.calls=[]
 def tearDown(self):self.tmp.cleanup()
 def call(self,id='test',send=None,body=None):
  b=body or {'model':r.MODEL,'messages':[]}
  return r.route_and_call(b,id,send or self.send,lambda _:None)
 def send(self,route,id,body):
  self.calls.append(route);return (429,'quota') if route=='go' else (200,'ok')
 def test_fallback_sticks_and_healthy_calls_are_free(self):
  for _ in range(12):self.assertEqual(self.call()[0],200)
  self.assertEqual(self.calls,['go']+['ollama']*12)
  self.assertEqual(r.state_for('test').recoveries,1)
 def test_budget_six_and_terminal(self):
  self.call()
  def flaky(route,id,body):
   self.calls.append(route)
   return (503,'fail') if len(self.calls)%2==1 else (200,'ok')
  self.calls=[]
  for _ in range(5):self.assertEqual(self.call(send=flaky)[0],200)
  self.assertEqual(r.state_for('test').recoveries,6)
  self.assertEqual(self.call(send=flaky)[0],503)
  before=len(self.calls);self.call(send=flaky);self.assertEqual(len(self.calls),before)
 def test_quota_on_both_no_retry(self):
  def bad(route,id,body):self.calls.append(route);return 429,'quota'
  self.assertEqual(self.call(send=bad)[0],429)
  self.assertEqual(self.calls,['go','ollama'])
  self.call(send=bad);self.assertEqual(len(self.calls),2)
 def test_one_transient_retry_per_route(self):
  def bad(route,id,body):self.calls.append(route);return 503,'bad'
  self.call(send=bad)
  self.assertEqual(self.calls,['go','go','ollama'])
 def test_persistent_route_and_budget(self):
  self.call();r.STATES.clear();self.call()
  self.assertEqual(self.calls,['go','ollama','ollama'])
  self.assertEqual(r.state_for('test').recoveries,1)
 def test_separate_executions(self):
  self.call('one');self.call('two')
  self.assertEqual(self.calls,['go','ollama','go','ollama'])
 def test_credentials_and_session_header(self):
  requests=[]
  class Response:
   status=200
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self):return b'{}'
  def capture(req,**kw):requests.append(req);return Response()
  with patch.dict(os.environ,{'OPENCODE_GO_API_KEY':'FAKE_GO','OLLAMA_API_KEY':'FAKE_OLLAMA'}),patch.object(r.urllib.request,'urlopen',capture):
   r.forward('go','identity',{'model':r.MODEL});r.forward('ollama','identity',{'model':r.MODEL})
  self.assertEqual(requests[0].get_header('Authorization'),'Bearer FAKE_GO')
  self.assertEqual(requests[1].get_header('Authorization'),'Bearer FAKE_OLLAMA')
  self.assertEqual(requests[0].get_header('X-opencode-session'),'identity')
  self.assertIsNone(requests[1].get_header('X-opencode-session'))
  self.assertTrue(all('openrouter' not in req.full_url for req in requests))
 def test_reject_missing_identity_and_other_model(self):
  self.assertEqual(self.call('')[0],400)
  self.assertEqual(r.route_and_call({'model':'glm-5.3-flash'},'test')[0],400)
 def tools_body(self):
  return {'model':r.MODEL,'messages':[],'tools':[{'function':{'name':'submit_review'}}]}
 def test_malformed_reasoning_only_counts_recovery_then_terminal(self):
  count={'n':0}
  def flaky(route,id,body):
   self.calls.append(route);count['n']+=1
   if count['n']==1:
    return 200,json.dumps({'choices':[{'message':{'role':'assistant','content':None},'finish_reason':'stop'}]})
   return 200,json.dumps({'choices':[{'message':{'role':'assistant','tool_calls':[{'type':'function','function':{'name':'submit_review','arguments':'{}'}}]}}]})
  self.assertEqual(self.call(send=flaky,body=self.tools_body())[0],200)
  self.assertEqual(r.state_for('test').recoveries,1)
  self.assertEqual(r.state_for('test').reason,'')
  def always_malformed(route,id,body):
   self.calls.append(route)
   return 200,json.dumps({'choices':[{'message':{'role':'assistant','content':None},'finish_reason':'stop'}]})
  self.assertEqual(self.call(send=always_malformed,body=self.tools_body())[0],503)
  self.assertTrue(r.state_for('test').failed)
  self.assertEqual(r.state_for('test').reason,'malformed_response_persistent')
  before=len(self.calls);self.call(send=always_malformed,body=self.tools_body());self.assertEqual(len(self.calls),before)
 def test_tools_call_with_content_is_accepted(self):
  def content(route,id,body):
   self.calls.append(route)
   return 200,json.dumps({'choices':[{'message':{'content':'{}'}}]})
  self.assertEqual(self.call(send=content,body=self.tools_body())[0],200)
  self.assertEqual(r.state_for('test').recoveries,0)
 def test_summary_records_calls_by_route(self):
  self.call()
  s=r.state_for('test').summary()
  self.assertEqual(s['calls_by_route']['go'],1)
  self.assertEqual(s['calls_by_route']['ollama'],1)

if __name__=='__main__':unittest.main(verbosity=2)
