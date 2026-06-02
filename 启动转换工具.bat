@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title 求生之路2 武器模型转换工具

set "PYTHON_EXE="
for /f "delims=" %%P in ('where python.exe 2^>nul') do (
    set "PYTHON_EXE=%%P"
    goto run_tool
)

echo 未找到 python.exe。
echo 请安装 Python 3，并确认在命令行输入 python 可以正常运行。
pause
exit /b 1

:run_tool
"%PYTHON_EXE%" "%~dp0weapon_porter.py"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo 工具启动失败，错误码：%EXITCODE%
    pause
)
exit /b %EXITCODE%
