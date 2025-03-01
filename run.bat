@echo off

REM 自动查找 backend 目录 (假设 run.bat 与 backend 在同一级)
set "BACKEND_DIR="
for /d %%a in ("%~dp0backend") do (
    set "BACKEND_DIR=%%~fa"
)



REM 切换到 backend 目录
cd /d "%BACKEND_DIR%"

REM 运行 python app.py
start "Backend" cmd /k "python app.py"


REM 设置 Python 解释器路径（如果需要虚拟环境，请激活）
set "PYTHON_EXECUTABLE=python"

REM --- 前端启动 ---
cd /d "%~dp0"
set "PROJECT_ROOT=%cd%"
set "MAX_LEVELS=5"  REM 设置最大向上查找层数

:find_frontend
set "FRONTEND_FOUND=0"
for /l %%i in (1, 1, %MAX_LEVELS%) do (
    if exist "%PROJECT_ROOT%\frontend\package.json" (
        set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
        set "FRONTEND_FOUND=1"
        goto :start_frontend
    )
    cd ..
    set "PROJECT_ROOT=%cd%"
)

:start_frontend
REM 进入前端目录
cd /d "%FRONTEND_DIR%"


REM 启动前端 (Vue.js 开发服务器)
start "Frontend" cmd /k "npm run serve"
