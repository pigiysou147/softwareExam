### 部署指南（Dify 1.7 + Ollama DeepSeek + MySQL 5.7）

#### 1. 准备环境
- 已安装 docker 与 docker compose（部署 Dify 建议）
- MySQL 5.7.44 可用
- 安装并运行 Ollama（用于 DeepSeek）

Ollama 安装与拉取模型：
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull deepseek-r1
ollama serve  # 默认 11434 端口
```

验证：
```bash
curl http://localhost:11434/api/tags | jq
```

#### 2. 启动本地服务（供 Dify 工作流调用）
在 `dify_data_assistant` 目录：
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn service.main:app --host 0.0.0.0 --port 8000 --reload
```

API：
- `POST /classify` 传入 MySQL 连接信息，返回分级结果与 Excel(base64)
- `POST /scrape` 将 URL 抓取为 Markdown（带缓存）

#### 3. Dify 1.7 安装与配置（简要）
参考官方仓库与文档，或使用 docker 方式：
```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
# 在 .env 中启用 OLLAMA 并设置地址
# CUSTOM_MODEL_ENABLED=true
# OLLAMA_API_BASE_URL=http://host.docker.internal:11434
docker compose up -d
```

浏览器访问 Dify 控制台，完成初始化。添加模型供应商：Ollama，添加 `deepseek-r1` 模型。

#### 4. 导入工作流
- 在 Dify 应用中，选择“导入”，选取 `workflows/classifier_workflow.yaml` 与 `workflows/scraper_optimized_workflow.yaml`
- 对于分类工作流，运行时输入 MySQL 连接信息；确保本地服务 8000 端口可访问（Docker 内访问宿主需使用 `host.docker.internal`）。

#### 5. 测试
- 在 MySQL 中导入测试库：
```bash
mysql -uroot -p < testdata/sample_schema.sql
```
- 运行工作流：传入连接 `host=<mysql_host> port=3306 user=<user> password=<pwd> database=demo_db`
- 成功后，下载生成的 `数据分级清单.xlsx`

#### 6. 常见问题
- Docker 网络下访问宿主服务：使用 `http://host.docker.internal:<port>`
- LLM 优化失败：服务将回退使用规则分类结果
- Excel 空表：检查数据库名是否正确、账号权限与 `INFORMATION_SCHEMA` 可见性

