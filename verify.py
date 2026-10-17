import json,urllib.request
base='http://127.0.0.1:18788'
def req(path,method='GET',body=None,token=None):
 d=json.dumps(body).encode() if body is not None else None
 h={'Content-Type':'application/json'}
 if token:h['Authorization']='Bearer '+token
 with urllib.request.urlopen(urllib.request.Request(base+path,data=d,headers=h,method=method),timeout=10) as r:return r.status,json.loads(r.read()) if path.startswith('/api/') else len(r.read())
health=req('/api/healthz')
try: reg=req('/api/auth/register','POST',{'username':'verify_user','password':'verify123','name':'验证用户'})
except Exception: reg=('existing',None)
login=req('/api/auth/login','POST',{'username':'verify_user','password':'verify123'})
tok=login[1]['data']['token']
me=req('/api/auth/me',token=tok)
events=req('/api/events?page=1&pageSize=3')
front=req('/')
print(json.dumps({'health':health[1]['code'],'register':reg[0],'login':login[1]['code'],'me':me[1]['data']['username'],'events':len(events[1]['data']['list']),'frontend_status':front[0],'frontend_bytes':front[1]},ensure_ascii=False))
