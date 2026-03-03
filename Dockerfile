# 使用 Python 3.11 稳定版本，避免 Python 3.14 的兼容性问题
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Render 可能使用 10000，但 Dockerfile 中保持 8000）
EXPOSE 8000

# 启动命令（使用环境变量 PORT，Render 会自动设置为 10000）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
