@echo off
chcp 65001 >nul
echo ========================================
echo   华为云ECS网站快速部署工具
echo ========================================
echo.

REM 检查是否提供了IP地址
if "%1"=="" (
    echo ❌ 错误：请提供ECS服务器的公网IP地址
    echo.
    echo 使用方法：
    echo    快速部署.bat 你的公网IP
    echo.
    echo 例如：
    echo    快速部署.bat 123.45.67.89
    echo.
    pause
    exit /b 1
)

set SERVER_IP=%1
echo 📋 部署信息：
echo    服务器IP: %SERVER_IP%
echo    用户名: root
echo.

REM 检查必要文件
echo 🔍 检查本地文件...
if not exist "index.html" (
    echo ❌ 错误：找不到 index.html 文件
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

if not exist "deploy.sh" (
    echo ❌ 错误：找不到 deploy.sh 文件
    pause
    exit /b 1
)

echo ✅ 文件检查通过
echo.

REM 检查SSH连接
echo 🔌 测试SSH连接...
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@%SERVER_IP% "echo 连接成功" 2>nul
if errorlevel 1 (
    echo ⚠️  警告：SSH连接测试失败
    echo.
    echo 可能的原因：
    echo 1. 安全组未开放22端口
    echo 2. IP地址错误
    echo 3. 首次连接需要手动确认
    echo.
    echo 是否继续尝试上传？[Y/N]
    set /p continue=
    if /i not "%continue%"=="Y" exit /b 1
)
echo.

REM 上传文件
echo 📤 步骤 1/3: 上传文件到服务器...
echo.
echo 上传 index.html...
scp index.html root@%SERVER_IP%:/root/
if errorlevel 1 (
    echo ❌ 上传失败
    pause
    exit /b 1
)

echo 上传 deploy.sh...
scp deploy.sh root@%SERVER_IP%:/root/
if errorlevel 1 (
    echo ❌ 上传失败
    pause
    exit /b 1
)

echo ✅ 文件上传完成
echo.

REM 设置执行权限并运行脚本
echo 🚀 步骤 2/3: 在服务器上运行部署脚本...
echo.
ssh root@%SERVER_IP% "chmod +x /root/deploy.sh && bash /root/deploy.sh"
if errorlevel 1 (
    echo ❌ 部署脚本执行失败
    pause
    exit /b 1
)

echo.
echo 🎉 步骤 3/3: 部署完成！
echo.
echo ========================================
echo   部署成功！
echo ========================================
echo.
echo 🌐 请在浏览器中访问：
echo    http://%SERVER_IP%
echo.
echo 📝 管理命令（在服务器SSH中执行）：
echo    systemctl status nginx    # 查看状态
echo    systemctl restart nginx   # 重启服务
echo.

REM 尝试打开浏览器
echo 是否在浏览器中打开网站？[Y/N]
set /p open_browser=
if /i "%open_browser%"=="Y" (
    start http://%SERVER_IP%
)

echo.
pause
