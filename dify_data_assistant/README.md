## 数据分级分类助手（基于 Dify 1.7 + Ollama DeepSeek + MySQL 5.7）

本项目提供一套可直接导入 Dify 的工作流配置与可落地的 Python 服务，用于：
- 从 MySQL 拉取库/表/字段结构
- 按分级分类规则为表与字段打标签（可选接入 DeepSeek 做智能修正）
- 生成 Excel 分级清单
- 附加：网页抓取到 Markdown 的优化流程（缓存加速）

### 目录结构
```
dify_data_assistant/
  README.md
  requirements.txt
  service/
    main.py
    db.py
    classifier.py
    excel.py
    scraper.py
  workflows/
    classifier_workflow.yaml
    scraper_optimized_workflow.yaml
  testdata/
    sample_schema.sql
    expected_classification_sample.csv
  docs/
    DEPLOYMENT.md
    DIFY_IMPORT.md
```

### 快速开始（本地运行服务）
1) 安装依赖
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
2) 启动服务（默认端口 8000）
```bash
uvicorn service.main:app --host 0.0.0.0 --port 8000 --reload
```
3) 打开 API 文档
```
http://localhost:8000/docs
```

### 与 Dify 集成
- 在 Dify 1.7 中：
  - 配置模型供应商：Ollama（`http://localhost:11434`），添加 `deepseek-r1:latest` 模型
  - 导入 `workflows/` 下的 YAML 工作流
  - 在应用变量里配置 MySQL 连接信息，或在运行时输入

更详细说明请参考 `docs/DEPLOYMENT.md` 与 `docs/DIFY_IMPORT.md`。

