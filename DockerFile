# 使用官方Python基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录到容器中
COPY . /app
EXPOSE 5000
# 设置Flask服务运行
CMD ["python", "app.py"]
