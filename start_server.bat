@echo off
chcp 65001 > nul
echo 正在启动本地Web服务器...
echo.
python -m http.server 8000
pause
