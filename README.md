# 21岁的我 - 聊天网页版

你的数字分身，朋友可以通过网页和你聊天。

## 目录结构

```
21-bot/
├── main.py          # FastAPI 后端
├── prompt.py        # 你的人格 prompt
├── requirements.txt # Python 依赖
├── .env.example     # 环境变量模板
├── railway.json     # Railway 配置
└── static/
    └── index.html   # 聊天界面
```

## 费用

DeepSeek API 极其便宜，50元/月预算完全够用：

| 模型 | 输入价格 | 输出价格 | 约可聊条数/月 |
|------|---------|---------|-------------|
| deepseek-v4-flash | ¥?/1M tokens | ¥?/1M tokens | ~充足 |

## 部署到 Railway（推荐，免费）

### 准备工作

1. **DeepSeek API Key**：去 https://platform.deepseek.com 注册 → 创建 API Key，充值 50元够用很久
2. **Railway 账号**：https://railway.app/ 用 GitHub 登录
3. **Git**（如果还没有）：https://git-scm.com/

### 部署步骤

```bash
# 1. 在项目目录初始化 git
cd 21-bot
git init
git add .
git commit -m "init"

# 2. 在 GitHub 新建一个私有仓库，把代码推上去

# 3. 在 Railway Dashboard → New Project → Deploy from GitHub repo
#    选择你刚创建的仓库

# 4. 在 Railway 项目设置中添加环境变量：
#    DEEPSEEK_API_KEY = 你的 DeepSeek API 密钥
#    BOT_PASSWORD     = 你设置的访问密码（分享给朋友）

# 5. 部署完成，Railway 会生成 `.railway.app` 域名，分享给朋友即可
```

## 本地测试

```bash
pip install -r requirements.txt

# Windows PowerShell:
$env:DEEPSEEK_API_KEY="你的密钥"
$env:BOT_PASSWORD="你的密码"
uvicorn main:app --reload --port 8000
```

浏览器打开 http://localhost:8000 即可。
