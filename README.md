# AI Capability Service

一个生产就绪的「模型能力统一调用」最小独立后端服务。

## 功能特性

- ✅ 统一的 API 接口：`POST /v1/capabilities/run`
- ✅ 支持能力：`text_summary`（文本摘要）、`text_translate`（文本翻译）
- ✅ 统一响应格式（成功/失败）
- ✅ 自动 API 文档（Swagger UI / ReDoc）
- ✅ 请求耗时统计
- ✅ 结构化日志记录
- ✅ 完整的错误处理
- ✅ 可选真实模型接入（OpenAI）
- ✅ 单元测试覆盖

## 快速开始

### 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 启动服务

**方式 1：使用启动脚本（推荐）**

```bash
# 在项目根目录执行
python run.py
```

**方式 2：使用 uvicorn 命令**

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**注意**：
- 不要直接运行 `python app/main.py`，这会导致模块导入错误
- `.env` 文件必须放在项目根目录下才能被正确加载

### 验证是否使用真实 API

调用接口后观察响应：
- **真实 API**: 耗时 >500ms，结果是智能生成的摘要/翻译
- **模拟模式**: 耗时 <10ms，结果是简单截断或标记 `[Summary truncated]`

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 备用文档：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

## API 使用示例

### 1. 文本摘要（text_summary）

```bash
curl -X POST http://localhost:8000/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "text_summary",
    "input": {
      "text": "这是一段需要被摘要的长文本。人工智能是计算机科学的一个分支，致力于创造能够执行通常需要人类智能的任务的机器。这些任务包括学习、推理、问题解决、感知和语言理解。AI 技术正在快速发展，并在医疗、金融、交通等多个领域得到广泛应用。",
      "max_length": 100
    },
    "request_id": "req-summary-001"
  }'
```

成功响应：
```json
{
  "ok": true,
  "data": {
    "result": {
      "result": "这是一段需要被摘要的长文本。人工智能是计算机科学的一个分支，致力于创造能够执行通常需要人类智能的任务的机器... [Summary truncated]"
    }
  },
  "meta": {
    "request_id": "req-summary-001",
    "capability": "text_summary",
    "elapsed_ms": 3
  }
}
```

### 2. 文本翻译（text_translate）

```bash
curl -X POST http://localhost:8000/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "text_translate",
    "input": {
      "text": "hello",
      "target_language": "zh",
      "source_language": "en"
    },
    "request_id": "req-translate-001"
  }'
```

成功响应：
```json
{
  "ok": true,
  "data": {
    "result": {
      "translated_text": "你好",
      "source_language": "en",
      "target_language": "zh",
      "note": "Translated using simulation mode"
    }
  },
  "meta": {
    "request_id": "req-translate-001",
    "capability": "text_translate",
    "elapsed_ms": 2
  }
}
```

### 3. 错误示例（未知能力）

```bash
curl -X POST http://localhost:8000/v1/capabilities/run \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "unknown_capability",
    "input": {}
  }'
```

错误响应：
```json
{
  "ok": false,
  "error": {
    "code": "CAPABILITY_NOT_FOUND",
    "message": "Capability 'unknown_capability' not found",
    "details": {
      "available_capabilities": ["text_summary", "text_translate"]
    }
  },
  "meta": {
    "request_id": "a1b2c3d4",
    "capability": "unknown_capability",
    "elapsed_ms": 1
  }
}
```

## 接入真实模型（可选）

如需接入 OpenAI 真实模型，设置环境变量：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，用于代理
OPENAI_MODEL=gpt-3.5-turbo  # 可选，指定模型
```

或使用环境变量直接启动：

```bash
OPENAI_API_KEY=sk-your-api-key uvicorn app.main:app --reload
```

## 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=app --cov-report=term-missing

# 详细输出
pytest -v
```

## 项目结构

```
├── app/
│   ├── __init__.py           # 包初始化
│   ├── main.py               # FastAPI 应用入口
│   ├── config.py             # 配置管理
│   ├── models.py             # Pydantic 数据模型
│   ├── handlers.py           # 能力处理器
│   ├── services.py           # 业务逻辑层
│   ├── exceptions.py         # 自定义异常
│   └── logging_config.py     # 日志配置
├── tests/
│   ├── __init__.py
│   └── test_api.py           # API 测试
├── requirements.txt          # 依赖列表
├── .env.example              # 环境变量示例
└── README.md                 # 本文档
```

## 响应格式说明

### 成功响应

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | `true` | 成功标识 |
| `data.result` | any | 能力执行结果 |
| `meta.request_id` | string | 请求 ID |
| `meta.capability` | string | 调用的能力名称 |
| `meta.elapsed_ms` | int | 执行耗时（毫秒） |

### 失败响应

| 字段 | 类型 | 说明 |
|------|------|------|
| `ok` | `false` | 失败标识 |
| `error.code` | string | 错误码 |
| `error.message` | string | 错误描述 |
| `error.details` | object | 额外错误信息 |
| `meta.*` | - | 同上 |

### 错误码

| 错误码 | 说明 |
|--------|------|
| `CAPABILITY_NOT_FOUND` | 请求的能力不存在 |
| `INVALID_INPUT` | 输入参数无效 |
| `MODEL_SERVICE_ERROR` | 模型服务调用失败 |
| `INTERNAL_ERROR` | 内部服务器错误 |

## 技术栈

- **FastAPI** - 高性能 Web 框架
- **Pydantic** - 数据验证与设置管理
- **Uvicorn** - ASGI 服务器
- **Pytest** - 测试框架

## License

MIT
