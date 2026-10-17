# 全球灵异事件处理总部 · GHOST PROTOCOL

“全球灵异事件处理总部”是一个以灵异事件、鬼域和驭鬼者世界观为核心的沉浸式互动网站。项目将灵异题材内容管理、事件监控、任务系统、社区交流和 RPG 成长机制整合在同一套指挥中心界面中。

本仓库包含网站公开前端源码归档，以及根据前端 API 调用和公开响应结构重建的可运行兼容后端。

## 网站内容

网站以虚构的全球灵异事件管理机构 **G.H.Q.（Global Paranormal Incident Management Headquarters）** 为背景，用户可作为总部成员浏览情报、参与社区并处理任务。

主要模块：

- 全球灵异事件监控与事件档案
- 鬼域地图、危险等级及扩散趋势
- 全球伤亡数据与区域情报统计
- 灵异事件上报与审核流程
- 总部任务派发、接取及成果提交
- 灵异物品库和知识库
- 驭鬼者等级、经验、排行榜及晋升申请
- 每日简报、广播和总部通知
- 论坛、社区动态、聊天、私信及投票
- 抽卡、签到、成就等游戏化功能
- 城市负责人、区域管理和秘书处信息
- 深空观测等世界观扩展页面

前端共提取出约 35 个页面路由和 131 个 API 路径，包括：

```text
/home                 总部首页
/monitor              全球事件监控
/events               灵异事件档案
/ghost-zone-map       鬼域地图
/casualties           全球伤亡统计
/regional-intel       区域情报
/tasks                任务派发
/report               事件上报
/artifacts            灵异物品库
/knowledge            知识库
/forum                论坛
/community            社区
/chat                 聊天
/gacha                抽卡
/leaderboard          排行榜
/daily-briefing       每日简报
/broadcast            总部广播
/secretariat          秘书处
/universe             深空观测
```

## 技术结构

### 前端

- 单页应用（SPA）和 Hash 路由
- HTML、CSS、JavaScript 主要内联在 `public/index.html`
- Leaflet 地图组件
- Bearer Token 登录状态
- 同源 REST API
- 联网和离线浏览逻辑
- 桌面端与移动端自适应布局

### 兼容后端

- Python 标准库实现，无第三方运行依赖
- SQLite 数据持久化
- 注册、登录、退出、Token 刷新及身份查询
- PBKDF2 密码哈希
- HMAC 签名 Bearer Token
- 通用 REST CRUD 和分页响应
- CORS 与 SPA 静态文件服务
- 统一响应格式：`{code, data, message}`
- 保存公开接口样本及 API 路径清单

## 项目目录

```text
.
├── public/
│   └── index.html               # 网站公开前端源码
├── fixtures/
│   ├── api_samples.json         # 公开 API 响应样本
│   └── api_surface.json         # 前端提取的 API 路径
├── server.py                    # Python + SQLite 兼容后端
├── verify.py                    # 注册、登录和接口联调脚本
├── start.bat                    # Windows 启动脚本
└── README.md
```

## 快速启动

需要 Python 3.8 或更高版本。

### Windows

```powershell
start.bat
```

### PowerShell / Linux / macOS

```bash
python server.py
```

访问：

```text
http://127.0.0.1:18788/#/monitor
```

默认管理账户：

```text
用户名：admin
密码：admin123
```

正式部署前设置环境变量：

```powershell
$env:GHQ_ADMIN_PASSWORD='NEW_PASSWORD'
$env:GHQ_SECRET='LONG_RANDOM_SECRET'
python server.py
```

可选配置：

```text
GHQ_HOST               监听地址，默认 127.0.0.1
GHQ_PORT               监听端口，默认 18788
GHQ_ADMIN_PASSWORD     初始管理员密码
GHQ_SECRET             Token 签名密钥
```

## 接口示例

```text
GET  /api/healthz
GET  /api/settings/about
GET  /api/home/stats
GET  /api/events?page=1&pageSize=20
GET  /api/ghost-zones?pageSize=200
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
```

运行验证：

```powershell
python verify.py
```

## 数据说明

仓库中的灵异事件、鬼域、伤亡数字、人物和组织均属于网站世界观及展示内容。兼容后端基于公开前端调用方式和公开 API 响应重建，不包含原服务器内部项目文件、私有数据库或未公开业务代码。

## License

兼容后端代码采用 [MIT License](LICENSE)。
