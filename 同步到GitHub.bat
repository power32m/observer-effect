@echo off
chcp 65001 >nul
echo ========================================
echo   同步到 GitHub Pages
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 添加文件到 git...
git add -A

echo.
echo [2/4] 提交更改...
git commit -m "更新章节内容"

echo.
echo [3/4] 推送到 GitHub...
git push origin main

echo.
echo [4/4] 完成！
echo.
echo 请访问: https://power32m.github.io/observer-effect/
echo.
pause
