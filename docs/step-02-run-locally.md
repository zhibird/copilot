# 步骤 02 - 本地运行并理解整体流程

## 1. 安装 Python 3.11（Windows）

1. 从官网下载安装 Python 3.11。
2. 安装过程中勾选 `Add Python to PATH`。
3. 在 PowerShell 中验证：

```powershell
python --version
```

## 2. 创建虚拟环境

```powershell
python -m venv .copilot
.\.copilot\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. 启动 API 服务

```powershell
uvicorn app.main:app --reload --port 8000
```

## 4. 验证接口（PowerShell 兼容写法）

### 4.1 健康检查

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/health"
```

### 4.2 创建团队

```powershell
$team = @{ team_id = "team_ops"; name = "Operations Team"; description = "MVP default team" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/teams" -ContentType "application/json" -Body $team
```

### 4.3 创建用户

```powershell
$user = @{ user_id = "u_001"; team_id = "team_ops"; display_name = "Alice"; role = "owner" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/users" -ContentType "application/json" -Body $user
```

### 4.4 导入文档

```powershell
$doc = @{
  team_id = "team_ops"
  source_name = "ops-guide.md"
  content_type = "md"
  content = "# Ops Guide`n`nAlways check alerts first. Escalate incidents quickly."
} | ConvertTo-Json

$imported = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/documents/import" -ContentType "application/json" -Body $doc
$document_id = $imported.document_id
```

### 4.5 文档切分

```powershell
$chunkPayload = @{ team_id = "team_ops"; max_chars = 120; overlap = 20 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/documents/$document_id/chunk" -ContentType "application/json" -Body $chunkPayload
```

### 4.6 建立向量索引

```powershell
$indexPayload = @{ team_id = "team_ops"; document_id = $document_id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/retrieval/index" -ContentType "application/json" -Body $indexPayload
```

### 4.7 TopK 检索

```powershell
$searchPayload = @{ team_id = "team_ops"; query = "alerts"; top_k = 3; document_id = $document_id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/retrieval/search" -ContentType "application/json" -Body $searchPayload
```

### 4.8 RAG 问答（chat/ask）

```powershell
$askPayload = @{
  user_id = "u_001"
  team_id = "team_ops"
  question = "出现告警后第一步要做什么？"
  top_k = 3
  document_id = $document_id
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/chat/ask" -ContentType "application/json" -Body $askPayload
```

## 5. 真实 LLM（可选）

默认 `LLM_PROVIDER=mock`，不依赖外部服务。

如果你要接真实模型，请在 `.env` 设置：

```env
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=你的key
LLM_MODEL=gpt-4.1-mini
```

## 6. 阅读代码顺序

1. `app/api/routes/chat.py`
2. `app/services/rag_chat_service.py`
3. `app/services/retrieval_service.py`
4. `app/services/llm_service.py`