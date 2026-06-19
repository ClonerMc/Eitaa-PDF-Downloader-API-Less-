# data/main/main_gui.py
import sys, os, subprocess, threading, urllib.request, json, time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QCheckBox,
    QProgressBar, QSpinBox, QTabWidget, QGroupBox, QLineEdit, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from downloader_core import EitaaWorkerThread

FA = "Tahoma"
FA_MONO = "Consolas"

DARK_QSS = f"""
QWidget {{ background-color: #1E1E2E; color: #CDD6F4; font-family: '{FA}'; font-size: 11pt; }}
QTabWidget::pane {{ border: 1px solid #313244; border-radius: 8px; background: #181825; }}
QTabBar::tab {{ background: #313244; color: #CDD6F4; padding: 10px 20px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
QTabBar::tab:selected {{ background: #89B4FA; color: #11111B; font-weight: bold; }}
QGroupBox {{ border: 1px solid #313244; border-radius: 8px; margin-top: 20px; font-weight: bold; padding-top: 15px; color: #89B4FA; }}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top right; padding: 0 10px; left: 10px; }}
QTextEdit {{ background-color: #11111B; border: 1px solid #313244; border-radius: 8px; padding: 10px; font-family: '{FA_MONO}'; color: #A6E3A1; font-size: 10pt; }}
QPushButton {{ background-color: #313244; color: #CDD6F4; border: none; border-radius: 6px; padding: 10px 15px; font-weight: bold; }}
QPushButton:hover {{ background-color: #45475A; }}
QPushButton:pressed {{ background-color: #585B70; }}
QPushButton:disabled {{ background-color: #181825; color: #585B70; }}
QLineEdit {{ background-color: #11111B; border: 1px solid #313244; border-radius: 6px; padding: 6px; color: #CDD6F4; }}
.BtnPrimary {{ background-color: #89B4FA; color: #11111B; }}
.BtnPrimary:hover {{ background-color: #B4BEFE; }}
.BtnSuccess {{ background-color: #A6E3A1; color: #11111B; }}
.BtnSuccess:hover {{ background-color: #94E2D5; }}
.BtnDanger {{ background-color: #F38BA8; color: #11111B; }}
.BtnDanger:hover {{ background-color: #FBA922; }}
.BtnHelp {{ background-color: #89B4FA; color: #11111B; border-radius: 6px; padding: 8px 15px; font-weight: bold; }}
.BtnHelp:hover {{ background-color: #B4BEFE; }}
.BtnLog {{ background-color: #F9E2AF; color: #11111B; font-weight: bold; }}
.BtnLog:hover {{ background-color: #F38BA8; }}
QProgressBar {{ border: 1px solid #313244; border-radius: 6px; text-align: center; background: #11111B; color: #CDD6F4; font-weight: bold; }}
QProgressBar::chunk {{ background-color: #89B4FA; border-radius: 5px; }}
QCheckBox {{ color: #CDD6F4; spacing: 8px; outline: none; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 2px solid #89B4FA; background: #11111B; }}
QCheckBox::indicator:checked {{ background: #89B4FA; image: url(check.png); }}
QSpinBox {{ background-color: #11111B; border: 1px solid #313244; border-radius: 6px; padding: 5px; color: #A6E3A1; font-weight: bold; min-height: 25px; }}
"""

class ModernEitaaGUI(QWidget):
    update_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.CURRENT_VERSION = "5.0"
        
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DARK_QSS)
        self.setWindowTitle("دانلودر PDF ایتا هوشمند")
        self.resize(950, 780)

        ico_path = os.path.join(os.path.dirname(__file__), "..", "img", "Ico.png")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        self.worker = EitaaWorkerThread()
        self.worker.log_signal.connect(self._log)
        self.worker.finished_signal.connect(self._on_done)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.browser_ready_signal.connect(self._on_browser_ready)
        
        self.update_signal.connect(self._on_update_result_received)

        self._build_ui()
        QTimer.singleShot(1500, self._auto_check_update)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_lbl = QLabel("دانلودر PDF ایتا هوشمند")
        title_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #89B4FA;")
        desc_lbl = QLabel(f"دانلود خودکار و ایجاد بانک اطلاعاتی از اسناد | نسخه {self.CURRENT_VERSION}")
        desc_lbl.setStyleSheet("color: #A6ADC8; font-size: 10pt;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(desc_lbl)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        logo_box = QVBoxLayout()
        img_dir = os.path.join(os.path.dirname(__file__), "..", "img")
        logo_path1 = os.path.join(img_dir, "logo.png")
        logo1 = QLabel()
        if os.path.exists(logo_path1):
            px1 = QPixmap(logo_path1).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
            logo1.setPixmap(px1)
            logo1.setFixedSize(px1.width(), px1.height())
        logo_box.addWidget(logo1, alignment=Qt.AlignmentFlag.AlignRight)

        logo_path2 = os.path.join(img_dir, "logo-s.png")
        logo2 = QLabel()
        if os.path.exists(logo_path2):
            px2 = QPixmap(logo_path2).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
            logo2.setPixmap(px2)
            logo2.setFixedSize(px2.width(), px2.height())
        logo_box.addWidget(logo2, alignment=Qt.AlignmentFlag.AlignRight)
        
        header_layout.addLayout(logo_box)
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_dashboard_tab(), "داشبورد عملیات")
        self.tabs.addTab(self._create_bot_settings_tab(), "تنظیمات پیشرفته")
        self.tabs.addTab(self._create_excel_settings_tab(), "مدیریت فایل و خروجی")
        main_layout.addWidget(self.tabs)

        self.btn_exit = QPushButton("❌ خروج امن و آزادسازی منابع سیستم")
        self.btn_exit.setStyleSheet("background:#F38BA8; color:#11111B; font-weight:bold; font-size: 12pt; padding: 12px; border-radius: 8px; margin-top: 5px;")
        self.btn_exit.clicked.connect(self.close)
        main_layout.addWidget(self.btn_exit)

        footer = QLabel("توسعه یافته توسط ابراهیم جوهری")
        footer.setStyleSheet("color: #6C7086; font-size: 10pt; font-weight: bold; margin-top: 5px;")
        main_layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

    def _create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top_ctrl_layout = QHBoxLayout()
        top_ctrl_layout.addWidget(QLabel("مراحل اجرا:", styleSheet="font-size: 13pt; font-weight: bold; color: #89B4FA;"))
        
        self.lbl_dashboard_update_notice = QLabel("")
        self.lbl_dashboard_update_notice.setStyleSheet("font-size: 12pt; font-weight: bold; color: #11111B; background: #F38BA8; padding: 5px 15px; border-radius: 6px;")
        self.lbl_dashboard_update_notice.setVisible(False)
        top_ctrl_layout.addWidget(self.lbl_dashboard_update_notice)

        top_ctrl_layout.addStretch()
        
        btn_help = QPushButton("❔ راهنمای نرم‌افزار")
        btn_help.setProperty("class", "BtnHelp")
        btn_help.clicked.connect(self._show_help_dialog)
        top_ctrl_layout.addWidget(btn_help)
        
        layout.addLayout(top_ctrl_layout)

        ctrl_group = QGroupBox()
        ctrl_layout = QHBoxLayout(ctrl_group)

        self.btn_browser = QPushButton("۱. اجرای مرورگر")
        self.btn_browser.setProperty("class", "BtnPrimary")
        self.btn_browser.clicked.connect(self._open_browser)
        
        self.btn_scan = QPushButton("۲. شروع استخراج")
        self.btn_scan.setProperty("class", "BtnSuccess")
        self.btn_scan.setEnabled(False)
        self.btn_scan.clicked.connect(self._start_scan)

        self.btn_stop = QPushButton("توقف عملیات")
        self.btn_stop.setProperty("class", "BtnDanger")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_scan)

        ctrl_layout.addWidget(self.btn_browser)
        ctrl_layout.addWidget(self.btn_scan)
        ctrl_layout.addWidget(self.btn_stop)
        layout.addWidget(ctrl_group)

        layout.addWidget(QLabel("گزارش وضعیت سیستم:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.log_box)

        self.pb = QProgressBar()
        self.pb.setValue(0)
        self.pb.setFormat("آماده به کار")
        layout.addWidget(self.pb)

        tools_layout = QHBoxLayout()
        btn_folder = QPushButton("📁 پوشه فایل‌ها")
        btn_folder.clicked.connect(lambda: os.startfile(os.path.abspath(self.worker.download_folder)) if os.path.exists(self.worker.download_folder) else None)
        
        btn_excel = QPushButton("📊 فایل گزارش (Excel)")
        btn_excel.clicked.connect(self._open_report)

        btn_dev_log = QPushButton("🐞 ذخیره لاگ برای توسعه‌دهنده")
        btn_dev_log.setProperty("class", "BtnLog")
        btn_dev_log.clicked.connect(self._export_dev_log)

        tools_layout.addWidget(btn_folder)
        tools_layout.addWidget(btn_excel)
        tools_layout.addWidget(btn_dev_log)
        layout.addLayout(tools_layout)

        return tab

    def _create_bot_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        group = QGroupBox("تنظیمات مرورگر و دانلود")
        grid = QGridLayout(group)
        grid.setSpacing(20)

        self.chk_headless = QCheckBox("اجرای مرورگر در پس‌زمینه (حالت مخفی)")
        self.chk_headless.toggled.connect(lambda v: setattr(self.worker, 'headless_mode', v))
        grid.addWidget(self.chk_headless, 0, 0, 1, 2)

        self.chk_quick = QCheckBox("تهیه لیست فایل‌ها بدون دانلود (صرفاً ثبت در اکسل)")
        self.chk_quick.toggled.connect(lambda v: setattr(self.worker, 'quick_mode', v))
        grid.addWidget(self.chk_quick, 1, 0, 1, 2)

        grid.addWidget(QLabel("تعداد صفحات برای بررسی پیام‌های قدیمی:"), 2, 0)
        self.spn_scroll = QSpinBox()
        self.spn_scroll.setRange(1, 200)
        self.spn_scroll.setValue(5)
        self.spn_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spn_scroll.valueChanged.connect(lambda v: setattr(self.worker, 'scroll_count', v))
        grid.addWidget(self.spn_scroll, 2, 1)
        
        grid.addWidget(QLabel("مکث بین هر صفحه (مناسب برای اینترنت کند):"), 3, 0)
        self.spn_delay = QSpinBox()
        self.spn_delay.setRange(1, 10)
        self.spn_delay.setValue(2)
        self.spn_delay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spn_delay.valueChanged.connect(lambda v: setattr(self.worker, 'scroll_delay', v))
        grid.addWidget(self.spn_delay, 3, 1)

        grid.addWidget(QLabel("تعداد دفعات تلاش مجدد در صورت خطا:"), 4, 0)
        self.spn_retry = QSpinBox()
        self.spn_retry.setRange(1, 5)
        self.spn_retry.setValue(2)
        self.spn_retry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spn_retry.valueChanged.connect(lambda v: setattr(self.worker, 'retry_count', v))
        grid.addWidget(self.spn_retry, 4, 1)

        layout.addWidget(group)

        update_group = QGroupBox("مرکز مدیریت به‌روزرسانی هوشمند")
        update_layout = QGridLayout(update_group)
        update_layout.setSpacing(15)

        self.chk_auto_update = QCheckBox("بررسی خودکار نسخه‌های جدید در هنگام شروع برنامه")
        self.chk_auto_update.setChecked(True)
        update_layout.addWidget(self.chk_auto_update, 0, 0, 1, 2)

        self.btn_manual_update = QPushButton("🔄 بررسی نسخه‌های جدید نرم‌افزار")
        self.btn_manual_update.setProperty("class", "BtnPrimary")
        self.btn_manual_update.clicked.connect(self._manual_check_update)
        update_layout.addWidget(self.btn_manual_update, 1, 0)

        self.lbl_update_status = QLabel("وضعیت: در حال بررسی...")
        update_layout.addWidget(self.lbl_update_status, 1, 1)

        layout.addWidget(update_group)
        layout.addStretch()
        return tab

    def _create_excel_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        path_group = QGroupBox("تنظیمات مسیر و فیلتر فایل")
        path_layout = QGridLayout(path_group)
        
        path_layout.addWidget(QLabel("مسیر ذخیره‌سازی:"), 0, 0)
        self.txt_path = QLineEdit(os.path.abspath(self.worker.download_folder))
        self.txt_path.setReadOnly(True)
        self.txt_path.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        btn_browse = QPushButton("تغییر مسیر")
        btn_browse.clicked.connect(self._browse_folder)
        path_layout.addWidget(self.txt_path, 0, 1)
        path_layout.addWidget(btn_browse, 0, 2)

        path_layout.addWidget(QLabel("فیلتر نام فایل (مثلاً: بخشنامه):"), 1, 0)
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("خالی = دانلود تمام فایل‌ها")
        self.txt_filter.textChanged.connect(lambda text: setattr(self.worker, 'keyword_filter', text.strip()))
        path_layout.addWidget(self.txt_filter, 1, 1, 1, 2)
        layout.addWidget(path_group)

        group = QGroupBox("تنظیمات ستون‌های اکسل")
        grid = QGridLayout(group)
        grid.setSpacing(15)

        self.chk_skip = QCheckBox("عدم دانلود فایل‌های تکراری")
        self.chk_skip.setChecked(True)
        self.chk_skip.toggled.connect(lambda v: setattr(self.worker, 'skip_duplicates', v))
        grid.addWidget(self.chk_skip, 0, 0)

        self.chk_link = QCheckBox("ایجاد لینک مستقیم برای دسترسی سریع")
        self.chk_link.setChecked(True)
        self.chk_link.toggled.connect(lambda v: setattr(self.worker, 'export_link', v))
        grid.addWidget(self.chk_link, 0, 1)

        self.chk_size = QCheckBox("درج حجم فایل")
        self.chk_size.setChecked(True)
        self.chk_size.toggled.connect(lambda v: setattr(self.worker, 'export_size', v))
        grid.addWidget(self.chk_size, 1, 0)

        self.chk_status = QCheckBox("درج وضعیت عملیات")
        self.chk_status.setChecked(True)
        self.chk_status.toggled.connect(lambda v: setattr(self.worker, 'export_status', v))
        grid.addWidget(self.chk_status, 1, 1)

        self.chk_date = QCheckBox("درج تاریخ و زمان")
        self.chk_date.setChecked(True)
        self.chk_date.toggled.connect(lambda v: setattr(self.worker, 'export_date', v))
        grid.addWidget(self.chk_date, 2, 0)

        self.chk_auto_open = QCheckBox("باز کردن فایل اکسل پس از اتمام کار")
        self.chk_auto_open.setChecked(True)
        grid.addWidget(self.chk_auto_open, 2, 1)

        layout.addWidget(group)
        layout.addStretch()
        return tab

    def _auto_check_update(self):
        if self.chk_auto_update.isChecked():
            threading.Thread(target=self._execute_update_check, args=(True,), daemon=True).start()
        else:
            self.lbl_update_status.setText("وضعیت: بررسی خودکار غیرفعال است.")
            self.lbl_update_status.setStyleSheet("color: #A6ADC8; font-weight: bold;")

    def _manual_check_update(self):
        self.btn_manual_update.setEnabled(False)
        self.btn_manual_update.setText("در حال بررسی...")
        self.lbl_update_status.setText("وضعیت: در حال اتصال به سرور گیت‌هاب...")
        self.lbl_update_status.setStyleSheet("color: #89DCEB;")
        threading.Thread(target=self._execute_update_check, args=(False,), daemon=True).start()

    def _execute_update_check(self, silent):
        nocache = str(int(time.time()))
        url = f"https://raw.githubusercontent.com/ClonerMc/Eitaa-PDF-Downloader-API-Less-/main/version.json?nc={nocache}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                data["silent"] = silent
                data["success"] = True
                self.update_signal.emit(data)
        except Exception:
            self.update_signal.emit({"success": False, "silent": silent})

    def _on_update_result_received(self, data):
        self.btn_manual_update.setEnabled(True)
        self.btn_manual_update.setText("🔄 بررسی نسخه‌های جدید نرم‌افزار")
        
        if not data.get("success", False):
            self.lbl_update_status.setText("وضعیت: خطا در اتصال به سرور.")
            self.lbl_update_status.setStyleSheet("color: #F38BA8; font-weight: bold;")
            if not data.get("silent", False):
                QMessageBox.warning(self, "خطای شبکه", "امکان اتصال به سرور گیت‌هاب فراهم نشد.\nلطفاً وضعیت شبکه را بررسی کنید.")
            return

        online_version = data.get("version", "5.0")
        update_msg = data.get("message", "")
        silent = data.get("silent", False)

        if online_version != self.CURRENT_VERSION:
            self.lbl_update_status.setText(f"نسخه جدید {online_version} یافت شد!")
            self.lbl_update_status.setStyleSheet("color: #F9E2AF; font-weight: bold;")
            
            self.lbl_dashboard_update_notice.setText(f"⚠️ آپدیت {online_version} در دسترس است! از تب تنظیمات بررسی کنید.")
            self.lbl_dashboard_update_notice.setVisible(True)
            
            if not silent:
                QMessageBox.information(
                    self, "به‌روزرسانی جدید", 
                    f"مهندس عزیز، نسخه جدید نرم‌افزار ({online_version}) منتشر شد.\n\nتغییرات:\n{update_msg}\n\nجهت دریافت فایل‌های جدید به کانال گیت‌هاب مراجعه فرمایید."
                )
        else:
            self.lbl_update_status.setText("وضعیت: آخرین نسخه روی سیستم شما نصب است.")
            self.lbl_update_status.setStyleSheet("color: #A6E3A1; font-weight: bold;")
            self.lbl_dashboard_update_notice.setVisible(False)
            if not silent:
                QMessageBox.information(self, "بررسی آپدیت", "نرم‌افزار شما کاملاً به‌روز است.")

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه ذخیره‌سازی")
        if folder:
            self.txt_path.setText(os.path.abspath(folder))
            self.worker.download_folder = folder

    def _export_dev_log(self):
        txt = self.log_box.toPlainText()
        if not txt:
            QMessageBox.warning(self, "خطا", "لاگی برای استخراج وجود ندارد.")
            return
        os.makedirs(self.worker.download_folder, exist_ok=True)
        log_path = os.path.join(self.worker.download_folder, f"Dev_Debug_Log_{datetime.now():%Y%m%d_%H%M%S}.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("=== Eitaa Downloader Debug Log ===\n")
            f.write(f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"Version: {self.CURRENT_VERSION}\n")
            f.write("Developer: Abrahim Johari\n")
            f.write("Contact: 09367056156\n")
            f.write("==================================\n\n")
            f.write(txt)
        QMessageBox.information(self, "لاگ ثبت شد", f"فایل عیب‌یابی با موفقیت ذخیره شد.\n\nمسیر فایل:\n{log_path}")

    def _install_prereqs(self):
        cmd = 'pip install playwright PyQt6 openpyxl pandas && playwright install chromium && echo. && echo [SUCCESS] All requirements verified/installed successfully! && pause'
        if os.name == 'nt':
            subprocess.Popen(f'start cmd /c "{cmd}"', shell=True)

    def _copy_prereqs(self):
        clipboard = QApplication.clipboard()
        clipboard.setText("pip install playwright PyQt6 openpyxl pandas && playwright install chromium")
        QMessageBox.information(self, "کپی شد", "دستورات با موفقیت کپی شدند.")

    def _show_help_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("راهنمای نرم‌افزار و رفع خطا")
        dlg.resize(680, 700)
        dlg.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        dlg.setStyleSheet(DARK_QSS)
        
        ico_path = os.path.join(os.path.dirname(__file__), "..", "img", "Ico.png")
        if os.path.exists(ico_path):
            dlg.setWindowIcon(QIcon(ico_path))
            
        layout = QVBoxLayout(dlg)
        
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        img_dir = os.path.join(os.path.dirname(__file__), "..", "img")
        logo_path1 = os.path.join(img_dir, "logo.png")
        logo_path2 = os.path.join(img_dir, "logo-s.png")
        
        logo1 = QLabel()
        if os.path.exists(logo_path1):
            px1 = QPixmap(logo_path1).scaledToWidth(110, Qt.TransformationMode.SmoothTransformation)
            logo1.setPixmap(px1)
            logo1.setFixedSize(px1.width(), px1.height())
        logo_layout.addWidget(logo1)
        
        logo2 = QLabel()
        if os.path.exists(logo_path2):
            px2 = QPixmap(logo_path2).scaledToWidth(140, Qt.TransformationMode.SmoothTransformation)
            logo2.setPixmap(px2)
            logo2.setFixedSize(px2.width(), px2.height())
        logo_layout.addWidget(logo2)
        
        layout.addLayout(logo_layout)

        text = QTextEdit()
        text.setReadOnly(True)
        
        content = """
        <div style="font-family: 'B Zar', 'B Nazanin', Tahoma; font-size: 15pt; line-height: 1.8; color: #CDD6F4; background-color: #11111B; padding: 15px; border-radius: 8px;">
            <h2 style='color: #89B4FA; font-family: Tahoma; font-size: 14pt; margin-bottom: 5px;'>راهنمای استفاده و پشتیبانی</h2>
            <ol>
                <li>ابتدا در صورت نیاز از بخش دکمه‌های زیر، پیش‌نیازهای سیستمی خود را بررسی یا نصب کنید.</li>
                <li>روی دکمه <b>«۱. اجرای مرورگر»</b> کلیک کنید.</li>
                <li>وارد حساب ایتا شوید و به کانال مورد نظر بروید.</li>
                <li>روی دکمه <b>«۲. شروع استخراج»</b> کلیک کنید تا عملیات آغاز شود.</li>
            </ol>
            <p style='color: #F38BA8; font-size: 14pt;'><b>عیب‌یابی:</b> در صورت بروز ارور، روی دکمه <i>«ذخیره لاگ برای توسعه‌دهنده»</i> کلیک کرده و فایل متنی را در ایتا، روبیکا یا تلگرام به شماره <b>09367056156</b> ارسال نمایید.</p>
            
            <hr style='border: 1px solid #313244; margin: 15px 0;'>
            
            <h3 style='color: #F9E2AF; font-family: Tahoma; font-size: 13pt; margin-bottom: 5px;'>درباره نرم‌افزار</h3>
            <p style='font-size: 14pt;'>
                <b>توسعه‌دهنده:</b> ابراهیم جوهری (دانشجوی مهندسی کامپیوتر نرم‌افزار)<br>
                <b>دانشکده:</b> دانشکده آموزش عالی زرند - دانشگاه شهید باهنر کرمان<br>
                <b>پروژه درس:</b> طراحی الگوریتم (استاد محترم: دکتر علی ناصر اسدی)<br>
                <b>مدیرگروه محترم:</b> استاد دکتر علی رهنما<br>
                <b>نسخه:</b> ۵.۰ (ویرایش هوشمند فول آپشن)
            </p>
        </div>
        """
        text.setHtml(content)
        layout.addWidget(text)

        btn_layout = QHBoxLayout()
        btn_close = QPushButton("بستن")
        btn_close.setStyleSheet("background-color: #313244; color: #CDD6F4; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_close.clicked.connect(dlg.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        dlg.exec()

    def closeEvent(self, event):
        try:
            if self.worker._browser: self.worker._browser.close()
            if self.worker._pw: self.worker._pw.stop()
        except: pass
        event.accept()

    def _log(self, str_msg, kind):
        colors = {"success": "#A6E3A1", "error": "#F38BA8", "warning": "#F9E2AF", "info": "#89DCEB"}
        color = colors.get(kind, "#CDD6F4")
        self.log_box.append(f"<span style='color:{color};'>{str_msg}</span>")
        
        if kind == "error" and "عملیات" not in str_msg:
            self.log_box.append("<span style='color:#F9E2AF; font-size: 10pt;'>💡 راهنما: در صورت قطعی یا خطا، روی «ذخیره لاگ برای توسعه‌دهنده» کلیک کرده و فایل را به <b>09367056156</b> (ابراهیم جوهری) ارسال کنید.</span>")
            
        self.log_box.ensureCursorVisible()

    def _on_progress(self, current, total):
        if total > 0:
            pct = int((current / total) * 100)
            self.pb.setValue(pct)
            self.pb.setFormat(f"پردازش: {current} از {total} (%p%)")

    def _on_browser_ready(self, success):
        if success:
            self.btn_browser.setText("✓ مرورگر با موفقیت اجرا شد")
            self.btn_browser.setEnabled(False)
            self.btn_scan.setEnabled(True)
            self.log_box.append("<br><b style='color:#F9E2AF;'>راهنما: وارد کانال ایتا شوید و سپس روی «شروع استخراج» کلیک کنید.</b><br>")
        else:
            self.btn_browser.setEnabled(True)
            self.btn_browser.setText("تلاش مجدد برای اجرای مرورگر")

    def _open_browser(self):
        self.btn_browser.setEnabled(False)
        self.btn_browser.setText("در حال اجرا...")
        self.worker.open_browser()

    def _start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.pb.setValue(0)
        self.worker.start_scan_and_download()

    def _stop_scan(self):
        self.worker.stop_process()
        self.btn_stop.setEnabled(False)

    def _open_report(self):
        if os.path.exists(self.worker.excel_path):
            os.startfile(os.path.abspath(self.worker.excel_path))
        else:
            QMessageBox.warning(self, "یافت نشد", "هنوز فایلی ایجاد نشده است.")

    def _on_done(self, status, count):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        if status == "success":
            self.pb.setValue(100)
            self.pb.setFormat(f"پایان: {count} فایل دریافت شد")
            QMessageBox.information(self, "گزارش", f"عملیات با موفقیت انجام شد.\nتعداد {count} فایل ثبت گردید.")
            if self.chk_auto_open.isChecked():
                self._open_report()
        elif status == "empty":
            QMessageBox.warning(self, "بدون تغییر", "فایل جدیدی یافت نشد.")
        elif status == "stopped":
            self.pb.setFormat("🛑 توقف توسط کاربر")
            QMessageBox.information(self, "لغو عملیات", "عملیات متوقف شد. فایل‌های قبلی ذخیره شده‌اند.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernEitaaGUI()
    window.show()
    sys.exit(app.exec())