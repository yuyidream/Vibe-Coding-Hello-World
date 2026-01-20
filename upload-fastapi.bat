@echo off
REM FastAPI 代码上传脚本 - Windows
REM 用途：将本地 FastAPI 代码上传到华为云 ECS

echo =========================================
echo FastAPI 代码上传到华为云 ECS
echo =========================================
echo.

REM 请根据实际情况修改以下变量
set SERVER_IP=123.249.68.162
set SERVER_USER=root
set REMOTE_PATH=/var/www/hello-world/backend-fastapi
set LOCAL_PATH=backend-fastapi

echo 注意：本脚本需要在服务器上先运行 deploy-fastapi.sh 创建目录
echo.
echo 请确保：
echo 1. 已在服务器上运行: bash deploy-fastapi.sh
echo 2. 已安装 WinSCP 或其他 SCP 工具
echo 3. 已配置 SSH 密钥或准备好输入密码
echo.
pause

echo.
echo 正在上传文件到服务器...
echo 目标服务器: %SERVER_IP%
echo 目标路径: %REMOTE_PATH%
echo.

REM 使用 scp 命令上传文件（需要 Git Bash 或安装 OpenSSH）
REM 如果没有 scp 命令，请使用 WinSCP 手动上传

echo 上传 app/__init__.py
scp "%LOCAL_PATH%/app/__init__.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/

echo 上传 app/main.py
scp "%LOCAL_PATH%/app/main.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/

echo 上传 app/config.py
scp "%LOCAL_PATH%/app/config.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/

echo 上传 app/database.py
scp "%LOCAL_PATH%/app/database.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/

echo 上传 app/dependencies.py
scp "%LOCAL_PATH%/app/dependencies.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/

echo 上传 app/models/__init__.py
scp "%LOCAL_PATH%/app/models/__init__.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/models/

echo 上传 app/routers/__init__.py
scp "%LOCAL_PATH%/app/routers/__init__.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/routers/

echo 上传 app/routers/public.py
scp "%LOCAL_PATH%/app/routers/public.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/routers/

echo 上传 app/routers/admin.py
scp "%LOCAL_PATH%/app/routers/admin.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/app/routers/

echo 上传 run.py
scp "%LOCAL_PATH%/run.py" %SERVER_USER%@%SERVER_IP%:%REMOTE_PATH%/

echo.
echo =========================================
echo 文件上传完成！
echo =========================================
echo.
echo 下一步操作：
echo 1. SSH 登录到服务器：ssh %SERVER_USER%@%SERVER_IP%
echo 2. 进入目录：cd /var/www/hello-world/backend-fastapi
echo 3. 启动服务：sudo -u www-data python3 run.py
echo 4. 测试 API：curl http://localhost:8001/api/health
echo.
pause
