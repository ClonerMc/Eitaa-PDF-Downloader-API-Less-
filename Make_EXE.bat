@echo off
chcp 65001 > nul
title EXE Builder
echo =======================================================
echo    در حال ساخت فایل اجرایی اختصاصی همراه با آیکون (Run_Eitaa.exe)
echo =======================================================
echo.

:: بررسی وجود فایل آیکون با فرمت استاندارد ico
if not exist "data\img\Ico.ico" (
    echo ⚠️ توجه: فایل آیکون با فرمت data\img\Ico.ico یافت نشد.
    echo برای قرارگیری آیکون روی فایل اصلی، ابتدا تصویر خود را به فرمت .ico تبدیل کرده و در این مسیر قرار دهید.
    echo.
)

echo using System; > src.cs
echo using System.Diagnostics; >> src.cs
echo using System.IO; >> src.cs
echo class App { >> src.cs
echo     static void Main() { >> src.cs
echo         string basePath = AppDomain.CurrentDomain.BaseDirectory; >> src.cs
echo         ProcessStartInfo p = new ProcessStartInfo(); >> src.cs
echo         string venv = Path.Combine(basePath, ".venv", "Scripts", "pythonw.exe"); >> src.cs
echo         if (File.Exists(venv)) { >> src.cs
echo             p.FileName = venv; >> src.cs
echo         } else { >> src.cs
echo             p.FileName = "pyw.exe"; >> src.cs
echo         } >> src.cs
echo         p.Arguments = @"data\main\launcher.pyw"; >> src.cs
echo         p.WorkingDirectory = basePath; >> src.cs
echo         p.WindowStyle = ProcessWindowStyle.Hidden; >> src.cs
echo         p.CreateNoWindow = true; >> src.cs
echo         p.UseShellExecute = false; >> src.cs
echo         try { Process.Start(p); } catch {} >> src.cs
echo     } >> src.cs
echo } >> src.cs

set COMPILER=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe
if not exist "%COMPILER%" set COMPILER=%WINDIR%\Microsoft.NET\Framework\v3.5\csc.exe

:: اضافه کردن خودکار پرچم  win32icon در صورت وجود فایل آیکون
if exist "data\img\Ico.ico" (
    "%COMPILER%" /nologo /target:winexe /win32icon:data\img\Ico.ico /out:Run_Eitaa.exe src.cs
) else (
    "%COMPILER%" /nologo /target:winexe /out:Run_Eitaa.exe src.cs
)

if exist src.cs del src.cs
echo.
echo ✓ فایل Run_Eitaa.exe با موفقیت و همراه با آیکون اختصاصی تولید شد.
echo.
pause
