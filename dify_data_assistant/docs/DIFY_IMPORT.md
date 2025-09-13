### 在 Dify 1.7 导入工作流

本仓库提供两个工作流：
- `workflows/classifier_workflow.yaml`：数据分级分类助手
- `workflows/scraper_optimized_workflow.yaml`：网页抓取到 Markdown（缓存）

#### 导入步骤
1. 登录 Dify 控制台，进入“工作流应用”
2. 选择“导入”，上传上述 YAML 文件
3. 打开工作流画布，检查节点与输出是否正常显示

#### 运行分类工作流
在“开始”节点输入变量：
- `db_host`：MySQL 地址（容器部署时，若 MySQL 在宿主机可用，可填写宿主机 IP）
- `db_port`：默认 3306
- `db_user`：数据库用户名
- `db_password`：数据库密码
- `db_name`：数据库名（例：demo_db）
- `refine_by_llm`：是否使用 DeepSeek（经 Ollama）做结果修正

运行后将得到一个文件输出，名称 `数据分级清单.xlsx`。

#### 运行抓取工作流
- 在“开始”节点填入 `url`
- 运行后返回 `markdown` 字段，可直接用于知识库入库

#### 注意
- 若 Dify 在 Docker 内运行，而本地服务在宿主机 8000 端口，YAML 中已配置使用 `http://host.docker.internal:8000` 进行调用。

