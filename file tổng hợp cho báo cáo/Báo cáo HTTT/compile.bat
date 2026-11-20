@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo   Đang biên dịch báo cáo LaTeX sang PDF...
echo ==============================================

where pdflatex >nul 2>nul
if %errorlevel% neq 0 (
    set "PATH=E:\MiTeX_installation\miktex\bin\x64;%PATH%"
)

echo [Lần 1] Chạy pdflatex...
pdflatex -interaction=nonstopmode "báo cáo HTTT.tex"

echo.
echo [Lần 2] Cập nhật mục lục, danh mục hình ảnh...
pdflatex -interaction=nonstopmode "báo cáo HTTT.tex"

echo.
if exist "báo cáo HTTT.pdf" (
    echo ==============================================
    echo   Biên dịch thành công! Đang mở file PDF...
    echo ==============================================
    start "" "báo cáo HTTT.pdf"
) else (
    echo [LỖI] Không tạo được file PDF. Vui lòng kiểm tra log.
)
pause
