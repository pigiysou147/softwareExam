## AI 数据分级分类助手（基于 DeepSeek + Dify）

本项目提供一个可直接部署与运行的示例：利用 DeepSeek（通过 Ollama 免费本地运行）与 Dify（低代码 AI 平台）协同，完成“数据库表结构分级分类打标并导出 Excel 清单”的智能体方案。适合作为学习与课程作业材料，覆盖模型部署、平台配置、知识库与工作流编排、以及端到端产出文件。

### 目标能力
- 深入理解并掌握 DeepSeek（开源大模型，Ollama 本地推理）与 Dify（低代码 AI 平台）的部署与使用
- 熟悉 Dify 的模型调用、HTTP 工具节点、变量/上下文传递、工作流编排
- 完成一个高频工作痛点案例：数据库分级分类助手
  - 输入：数据库连接信息
  - 过程：自动拉取表结构 → LLM 根据分级规则判定敏感级别与标签 → 导出 Excel 清单
  - 输出：Excel 分级清单（包含库名、表名、字段、分级/标签等）

### 目录结构
```text
ai-db-classifier/
  ├─ docker-compose.yml                  # 一键启动：Ollama + Postgres 示例库 + FastAPI 工具服务
  ├─ fastapi_service/                    # 提供“拉取表结构 / 生成Excel / 一体化流水线”HTTP接口
  │   ├─ app/
  │   │   ├─ main.py
  │   │   ├─ classifier.py
  │   │   └─ excel_utils.py
  │   ├─ requirements.txt
  │   └─ Dockerfile
  ├─ sample_db/
  │   └─ init.sql                        # 示例数据库结构与少量数据（容器启动自动导入）
  ├─ dify/
  │   └─ db_classification_workflow.json # 可直接导入 Dify 的工作流配置（含 HTTP+LLM+导出）
  ├─ tests/
  │   └─ schema_policy.json              # 示例分级规则（可在 Dify 或服务端使用）
  ├─ scripts/
  │   └─ run_local_test.sh               # 本地快速跑通：直接生成 Excel 输出
  └─ outputs/.gitkeep                    # 结果输出目录（容器挂载）
```

### 快速开始
1. 安装 Docker 与 Docker Compose。
2. 启动本项目依赖：
```bash
cd ai-db-classifier
docker compose up -d --build
```
首次启动会自动拉取并缓存 DeepSeek 模型（默认 deepseek-r1:7b），时间取决于网络环境。

3. 验证 FastAPI 工具服务：
```bash
curl -s http://localhost:8000/health
```

4. 直接本地端到端生成 Excel（不经 Dify，便于先验收效果）：
```bash
bash scripts/run_local_test.sh
```
完成后在 `outputs/` 目录可看到 Excel 清单文件。

#### 无 Docker 本地运行（可选）
若当前环境无 Docker，也可直接运行服务：
```bash
cd ai-db-classifier
bash scripts/run_service_locally.sh
```
启动后访问：
```bash
curl -s http://localhost:8000/health
```
然后执行一次端到端：
```bash
curl -s -X POST http://localhost:8000/classify_and_export \
  -H 'Content-Type: application/json' \
  -d '{
    "database_url": "postgresql+psycopg://dify:dify@localhost:5432/difydb",
    "policy_text": "根据字段名识别PII、支付、凭证等，输出level与tags",
    "output_filename": "sample_db_classification.xlsx"
  }'
```
注意：本地运行需要你自备 Postgres，并确保 `database_url` 可连通。

### 将 DeepSeek 接入 Dify
在 Dify 管理台：
- 模型接入 → 选择“OpenAI 兼容”
  - Base URL: `http://ollama:11434/v1`（若 Dify 与本项目处于同一 docker 网络）
  - 或 `http://localhost:11434/v1`（若本机 Dify 直接访问宿主机 Ollama）
  - API Key: 任意非空字符串（如 `ollama`）
  - Model Name: `deepseek-r1:7b`

> 说明：Ollama 提供 OpenAI 兼容接口，Dify 可将其视为“OpenAI 兼容”提供方。

### 导入 Dify 工作流
1. 在 Dify 创建“工作流应用”。
2. 进入工作流编辑器，右上角“导入”，选择本仓库 `dify/db_classification_workflow.json`。
3. 配置工作流中的变量：
   - `database_url`（示例已默认：`postgresql://dify:dify@postgres:5432/difydb`）
   - `policy_text`（可粘贴 `tests/schema_policy.json` 中规则段落，或自定义）
4. 确保模型节点选择 `deepseek-r1:7b`（OpenAI 兼容）。
5. 运行工作流，输出会返回 Excel 文件路径与预览前几行（同时文件在 `outputs/`）。

若导入 JSON 失败（因版本或 schema 差异），可在工作流中手动按以下节点搭建：
- 输入节点：`database_url`, `policy_text`
- HTTP 节点（POST `http://schema-service:8000/introspect`）传入 `{"database_url": "{{inputs.database_url}}"}`，结果命名为 `schemaResp`
- LLM 节点（OpenAI 兼容，模型 `deepseek-r1:7b`）：提示词使用 `schemaResp.body.schema` 与 `inputs.policy_text` 并要求仅输出 JSON 数组
- HTTP 节点（POST `http://schema-service:8000/export-excel`）传入 `{"classification": {{llmContent}}, "output_filename": "db_classification.xlsx"}`
- 输出节点：返回 `exportResp.body.file_path` 与 `llmContent[0:5]`

### 项目组件说明
- Ollama（容器）：本地运行 DeepSeek 模型，走 CPU 或 GPU（取决于设备）。
- FastAPI 工具服务：
  - `/introspect`：读取数据库表结构（通过 SQLAlchemy 反射）
  - `/classify`：调用 LLM（OpenAI 兼容接口）对表字段进行分级与标签判定
  - `/export-excel`：将分类结果导出 Excel
  - `/classify_and_export`：一键完成以上三步并返回文件
- Postgres 示例库：用于演示；你也可以传入自己的 `database_url`。

### 自定义与扩展
- 替换模型：可在 `docker-compose.yml` 中修改 `LLM_MODEL` 为其他可用的 DeepSeek/Ollama 模型（如 `deepseek-coder:6.7b`）。
- 接入私有数据库：向 `/introspect` 传入你的 `database_url`（注意网络与白名单）。
- 提升准确率：可在 `tests/schema_policy.json` 中细化分级策略，或在 Dify LLM 节点里优化提示词。

### 成果物
- 可交付文件：
  - Dify 工作流导入文件：`dify/db_classification_workflow.json`
  - 端到端 Excel 输出样例：运行后在 `outputs/` 自动生成
  - 文档材料：本 `README.md` 与注释完善的服务代码

### 常见问题
- 首次拉模型慢：可提前执行 `docker compose run --rm ollama-init` 预拉取。
- Dify 无法连到 Ollama：请确认 Dify 和本项目处于同一网络，或将 Base URL 指向宿主机端口 `http://localhost:11434/v1`。
- 结果为空或格式不对：可调用 `/classify` 时增加 `temperature` 或改进提示词；或在 `classifier.py` 中调整解析逻辑。

