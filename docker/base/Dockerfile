# 自定义基础镜像：本地化 Python 3.13-slim
#
# 用途：quiz 项目本地 Docker 构建统一基于此镜像，避免重复拉取 + 内嵌阿里云 pip 配置。
# 来源：Docker Hub `python:3.13-slim`（已通过外网代理预拉到本地）。
# 构建：docker build -t quiz-base:3.13 -f docker/base/Dockerfile docker/base
#
# 注意：quiz 项目 Dockerfile 应 `FROM quiz-base:3.13`，不要再写 pip 源配置（已在此固化）。
FROM python:3.13-slim

# 时区固化（quiz 项目依赖 TZ=Asia/Shanghai）
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timeinfo

# 固化阿里云 pip 镜像源（避免每次构建重复配置，也避免容器内安装走 PyPI 慢/不稳）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com