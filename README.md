# GHQ 兼容后端

零第三方依赖：Python 标准库 + SQLite。接口统一返回 `{code,data,message}`。

## 启动

```powershell
python server.py
```

浏览器访问 `http://127.0.0.1:18788/#/monitor`。

默认管理账号：`admin` / `admin123`。部署前通过环境变量修改：

```powershell
$env:GHQ_ADMIN_PASSWORD='NEW_PASSWORD'
$env:GHQ_SECRET='LONG_RANDOM_SECRET'
python server.py
```

实现：静态前端、注册、登录、Bearer Token、用户查询、SQLite 通用 CRUD、分页、CORS、真实公开接口样本兼容响应。未取得的业务数据端点返回统一空分页结构，写操作会存入 `ghq.sqlite3`。
