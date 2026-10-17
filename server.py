import base64, hashlib, hmac, json, mimetypes, os, secrets, sqlite3, time, uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
DB = os.path.join(ROOT, "ghq.sqlite3")
SECRET = os.environ.get("GHQ_SECRET", "change-this-ghq-secret").encode()
HOST = os.environ.get("GHQ_HOST", "127.0.0.1")
PORT = int(os.environ.get("GHQ_PORT", "18788"))

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.executescript("""
    create table if not exists users(id text primary key,username text unique,password_hash text,name text,role text,created_at integer);
    create table if not exists records(id text primary key,route text,data text,created_at integer,updated_at integer);
    """); return c

def passhash(password, salt=None):
    salt=salt or secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,120000)
    return base64.urlsafe_b64encode(salt+digest).decode()

def passok(password, encoded):
    raw=base64.urlsafe_b64decode(encoded); return hmac.compare_digest(passhash(password,raw[:16]),encoded)

def token(uid, ttl=86400):
    payload=base64.urlsafe_b64encode(json.dumps({"sub":uid,"exp":int(time.time())+ttl},separators=(",",":")).encode()).decode().rstrip("=")
    sig=base64.urlsafe_b64encode(hmac.new(SECRET,payload.encode(),hashlib.sha256).digest()).decode().rstrip("=")
    return payload+"."+sig

def token_uid(value):
    try:
        p,s=value.split(".",1); want=base64.urlsafe_b64encode(hmac.new(SECRET,p.encode(),hashlib.sha256).digest()).decode().rstrip("=")
        if not hmac.compare_digest(s,want): return None
        d=json.loads(base64.urlsafe_b64decode(p+"="*(-len(p)%4))); return d["sub"] if d["exp"]>=time.time() else None
    except: return None

def ok(data=None, message="success"): return {"code":0,"data":data,"message":message}
def fail(message="request failed", code=1): return {"code":code,"data":None,"message":message}
def page(items, q):
    page=max(1,int(q.get("page",[1])[0])); size=max(1,min(200,int(q.get("pageSize",q.get("limit",[20]))[0])))
    start=(page-1)*size; chunk=items[start:start+size]; total=len(items)
    return {"list":chunk,"items":chunk,"records":chunk,"total":total,"page":page,"pageSize":size,"totalPages":max(1,(total+size-1)//size),"hasMore":start+size<total}

FIX={}
sample=os.path.join(ROOT,"fixtures","api_samples.json")
if os.path.exists(sample):
    for x in json.load(open(sample,encoding="utf-8")):
        if x.get("status")==200 and isinstance(x.get("body"),dict): FIX[urlparse(x["path"]).path]=x["body"]

class App(BaseHTTPRequestHandler):
    server_version="GHQ-Compatible/1.0"
    def log_message(self, fmt, *args): print(time.strftime("%Y-%m-%d %H:%M:%S"),self.address_string(),fmt%args)
    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Authorization, Content-Type"); self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,PATCH,DELETE,OPTIONS")
    def send_json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.cors(); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def body(self):
        try: return json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
        except: return {}
    def uid(self):
        a=self.headers.get("Authorization",""); return token_uid(a[7:]) if a.startswith("Bearer ") else None
    def do_OPTIONS(self): self.send_response(204); self.cors(); self.end_headers()
    def do_GET(self): self.route("GET")
    def do_POST(self): self.route("POST")
    def do_PUT(self): self.route("PUT")
    def do_PATCH(self): self.route("PATCH")
    def do_DELETE(self): self.route("DELETE")
    def route(self,method):
        u=urlparse(self.path); path=u.path; q=parse_qs(u.query)
        if not path.startswith("/api/"): return self.static(path)
        if path=="/api/auth/register-policy": return self.send_json(ok({"ipLimit":3,"windowHours":24,"unlimited":True,"used":0,"remaining":3,"blocked":False,"exceeded":False,"ip":self.client_address[0]}))
        if path=="/api/auth/register" and method=="POST":
            b=self.body(); username=str(b.get("username") or b.get("account") or "").strip(); password=str(b.get("password") or "")
            if len(username)<2 or len(password)<6: return self.send_json(fail("用户名至少2位，密码至少6位"),400)
            uid="u-"+uuid.uuid4().hex[:12]; name=str(b.get("name") or b.get("nickname") or username)
            try:
                with db() as c: c.execute("insert into users values(?,?,?,?,?,?)",(uid,username,passhash(password),name,"user",int(time.time())))
            except sqlite3.IntegrityError: return self.send_json(fail("用户名已存在"),409)
            return self.send_json(ok({"token":token(uid),"user":{"id":uid,"uid":uid,"username":username,"name":name,"role":"user"}}))
        if path in ("/api/auth/login","/api/auth/admin-login") and method=="POST":
            b=self.body(); username=str(b.get("username") or b.get("account") or ""); password=str(b.get("password") or "")
            with db() as c: row=c.execute("select * from users where username=?",(username,)).fetchone()
            if not row or not passok(password,row["password_hash"]): return self.send_json(fail("用户名或密码错误"),401)
            user={"id":row["id"],"uid":row["id"],"username":row["username"],"name":row["name"],"role":row["role"]}
            return self.send_json(ok({"token":token(row["id"]),"accessToken":token(row["id"]),"user":user}))
        if path=="/api/auth/me":
            uid=self.uid()
            if not uid: return self.send_json(fail("unauthorized",401),401)
            with db() as c: row=c.execute("select * from users where id=?",(uid,)).fetchone()
            if not row: return self.send_json(fail("unauthorized",401),401)
            return self.send_json(ok({"id":row["id"],"uid":row["id"],"username":row["username"],"name":row["name"],"role":row["role"]}))
        if path in ("/api/auth/logout","/api/auth/refresh"):
            return self.send_json(ok({"token":token(self.uid())} if path.endswith("refresh") and self.uid() else True))
        if method=="GET" and path in FIX: return self.send_json(FIX[path])
        with db() as c:
            if method=="GET":
                rows=c.execute("select data from records where route=? order by created_at desc",(path,)).fetchall(); items=[json.loads(x[0]) for x in rows]
                return self.send_json(ok(page(items,q)))
            b=self.body(); rid=str(b.get("id") or uuid.uuid4()); now=int(time.time()); b["id"]=rid
            if method=="DELETE": c.execute("delete from records where id=? or (route=? and id=?)",(path.rsplit("/",1)[-1],path,path.rsplit("/",1)[-1])); return self.send_json(ok(True))
            c.execute("insert into records(id,route,data,created_at,updated_at) values(?,?,?,?,?) on conflict(id) do update set data=excluded.data,updated_at=excluded.updated_at",(rid,path,json.dumps(b,ensure_ascii=False),now,now))
            return self.send_json(ok(b))
    def static(self,path):
        if path in ("","/"): path="/index.html"
        full=os.path.abspath(os.path.join(PUBLIC,path.lstrip("/")))
        if not full.startswith(os.path.abspath(PUBLIC)) or not os.path.isfile(full): full=os.path.join(PUBLIC,"index.html")
        try:
            b=open(full,"rb").read(); self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(full)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
        except FileNotFoundError: self.send_error(404)

def init():
    with db() as c:
        if not c.execute("select 1 from users where username='admin'").fetchone():
            c.execute("insert into users values(?,?,?,?,?,?)",("u-admin","admin",passhash(os.environ.get("GHQ_ADMIN_PASSWORD","admin123")),"总部管理员","admin",int(time.time())))

if __name__=="__main__":
    init(); print(f"GHQ backend: http://{HOST}:{PORT}  admin/admin123"); ThreadingHTTPServer((HOST,PORT),App).serve_forever()
