@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: =====================================================
:: Hello World 子域名部署脚本
:: 域名: helloworld.renxinayi.com
:: =====================================================

echo =========================================
echo Hello World 子域名部署
echo 目标域名: helloworld.renxinayi.com
echo =========================================
echo.

:: 检查参数
if "%1"=="" (
    echo 用法: %0 服务器IP
    echo 示例: %0 123.249.68.162
    pause
    exit /b 1
)

set SERVER_IP=%1
set SERVER_USER=root

echo 服务器IP: %SERVER_IP%
echo.

:: =====================================================
:: 步骤 0: 检查DNS
:: =====================================================
echo [0/7] 检查DNS配置...
nslookup helloworld.renxinayi.com >nul 2>&1
if errorlevel 1 (
    echo.
    echo [警告] DNS未配置或未生效！
    echo.
    echo 请先在域名服务商添加A记录：
    echo   类型: A
    echo   主机记录: helloworld
    echo   记录值: %SERVER_IP%
    echo   TTL: 600
    echo.
    choice /C YN /M "是否继续（DNS稍后生效）"
    if errorlevel 2 exit /b 1
) else (
    echo [✓] DNS已生效
)
echo.

:: =====================================================
:: 步骤 1: 更新前端主页配置
:: =====================================================
echo [1/7] 更新前端主页配置...
cd frontend

if not exist ".env.production" (
    echo [错误] 找不到 .env.production
    cd ..
    pause
    exit /b 1
)

:: 备份原配置
copy .env.production .env.production.backup >nul 2>&1

:: 更新API地址
echo VITE_API_BASE_URL=https://helloworld.renxinayi.com/api> .env.production

echo [✓] 主页配置已更新
echo.

:: =====================================================
:: 步骤 2: 更新管理后台配置
:: =====================================================
echo [2/7] 更新管理后台配置...
cd ..\frontend-admin

if not exist ".env.production" (
    echo [错误] 找不到 .env.production
    cd ..
    pause
    exit /b 1
)

:: 备份原配置
copy .env.production .env.production.backup >nul 2>&1

:: 更新API地址
echo VITE_API_BASE_URL=https://helloworld.renxinayi.com/api> .env.production

echo [✓] 管理后台配置已更新
echo.

cd ..

:: =====================================================
:: 步骤 3: 构建前端主页
:: =====================================================
echo [3/7] 构建前端主页...
cd frontend

call npm run build
if errorlevel 1 (
    echo [错误] 前端构建失败
    cd ..
    pause
    exit /b 1
)

echo [✓] 主页构建完成
echo.

cd ..

:: =====================================================
:: 步骤 4: 构建管理后台
:: =====================================================
echo [4/7] 构建管理后台...
cd frontend-admin

call npm run build
if errorlevel 1 (
    echo [错误] 管理后台构建失败
    cd ..
    pause
    exit /b 1
)

echo [✓] 管理后台构建完成
echo.

cd ..

:: =====================================================
:: 步骤 5: 上传前端文件
:: =====================================================
echo [5/7] 上传前端文件到服务器...

echo 上传主页...
scp -r frontend\dist\* %SERVER_USER%@%SERVER_IP%:/www/wwwroot/hello-world/frontend/
if errorlevel 1 (
    echo [错误] 主页上传失败
    pause
    exit /b 1
)

echo 上传管理后台...
scp -r frontend-admin\dist\* %SERVER_USER%@%SERVER_IP%:/www/wwwroot/hello-world/frontend-admin/
if errorlevel 1 (
    echo [错误] 管理后台上传失败
    pause
    exit /b 1
)

echo [✓] 文件上传完成
echo.

:: =====================================================
:: 步骤 6: 上传Nginx配置
:: =====================================================
echo [6/7] 上传Nginx配置...

scp nginx_helloworld_subdomain.conf %SERVER_USER%@%SERVER_IP%:/tmp/
if errorlevel 1 (
    echo [错误] Nginx配置上传失败
    pause
    exit /b 1
)

echo [✓] Nginx配置已上传
echo.

:: =====================================================
:: 步骤 7: 配置服务器
:: =====================================================
echo [7/7] 配置服务器...
echo.
echo [注意] 接下来需要手动执行以下命令：
echo.
echo # 1. 申请SSL证书（如果DNS已生效）
echo sudo certbot certonly --nginx -d helloworld.renxinayi.com
echo.
echo # 2. 安装Nginx配置
echo sudo cp /tmp/nginx_helloworld_subdomain.conf /etc/nginx/sites-available/helloworld.conf
echo sudo ln -sf /etc/nginx/sites-available/helloworld.conf /etc/nginx/sites-enabled/
echo.
echo # 3. 测试并重载Nginx
echo sudo nginx -t
echo sudo systemctl reload nginx
echo.
echo # 4. 设置文件权限
echo sudo chown -R www-data:www-data /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin
echo sudo chmod -R 755 /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin
echo.

:: =====================================================
:: 完成
:: =====================================================
echo.
echo =========================================
echo 部署准备完成！
echo =========================================
echo.
echo 下一步：
echo 1. SSH登录服务器: ssh %SERVER_USER%@%SERVER_IP%
echo 2. 申请SSL证书: sudo certbot certonly --nginx -d helloworld.renxinayi.com
echo 3. 安装Nginx配置: sudo cp /tmp/nginx_helloworld_subdomain.conf /etc/nginx/sites-available/helloworld.conf
echo 4. 启用配置: sudo ln -sf /etc/nginx/sites-available/helloworld.conf /etc/nginx/sites-enabled/
echo 5. 测试: sudo nginx -t
echo 6. 重载: sudo systemctl reload nginx
echo 7. 设置权限: sudo chown -R www-data:www-data /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin
echo.
echo 完成后访问: https://helloworld.renxinayi.com/
echo.

choice /C YN /M "是否立即SSH到服务器执行配置"
if errorlevel 2 goto end
if errorlevel 1 ssh %SERVER_USER%@%SERVER_IP%

:end
pause
