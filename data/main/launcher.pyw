# data/main/launcher.pyw
import sys, os, ctypes, traceback

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CORE_DIR = os.path.join(BASE_DIR, "data", "core")
MAIN_DIR = os.path.join(BASE_DIR, "data", "main")
IMG_DIR  = os.path.join(BASE_DIR, "data", "img")

if CORE_DIR not in sys.path: sys.path.append(CORE_DIR)
if MAIN_DIR not in sys.path: sys.path.append(MAIN_DIR)

os.chdir(BASE_DIR)

try:
    from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QCheckBox, QSplashScreen
    from PyQt6.QtCore import Qt, QTimer, QCoreApplication
    from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
except ImportError as e:
    msg = f"کتابخانه‌های گرافیکی نصب نیستند.\nلطفا در CMD اجرا کنید:\npip install PyQt6 playwright pandas openpyxl"
    ctypes.windll.user32.MessageBoxW(0, msg, "Dependency Error", 0x10 | 0x0)
    sys.exit(1)

DARK_QSS = """
QWidget { background-color: #1E1E2E; color: #CDD6F4; font-family: 'Tahoma'; font-size: 11pt; }
QTextEdit { background-color: #11111B; border: 1px solid #313244; border-radius: 8px; padding: 15px; color: #CDD6F4; font-size: 11pt; line-height: 1.8; }
QPushButton { border: none; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 12pt; }
"""

class WelcomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("توافق‌نامه سطح کاربر (EULA) و سلب مسئولیت حقوقی")
        self.setFixedSize(750, 650)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DARK_QSS)
        
        ico_path = os.path.join(IMG_DIR, "Ico.png")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
            
        layout = QVBoxLayout(self)
        title = QLabel("قوانین، سیاست‌ها و شرایط استفاده از نرم‌افزار")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #89B4FA; margin-bottom: 5px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        text = QTextEdit()
        text.setReadOnly(True)
        content = """
        <div style="font-family: 'B Zar', 'B Nazanin', Tahoma;">
            <p style='color: #F38BA8; font-weight: bold; font-size: 15pt; margin-top: 0;'>⚠️ اخطار حقوقی: استفاده از این نرم‌افزار منوط به پذیرش دقیق شرایط زیر است:</p>
            <ul style='font-size: 14pt; margin-bottom: 20px;'>
                <li><b>مجوز استفاده:</b> این نرم‌افزار منحصراً جهت مقاصد <b>آموزشی، پژوهشی و آکادمیک</b> توسعه یافته است. استفاده از آن برای اهداف تجاری یا مخرب اکیداً ممنوع می‌باشد.</li>
                <li><b>حریم خصوصی و کپی‌رایت:</b> استخراج هرگونه سند از گروه‌ها و کانال‌ها باید با رعایت کامل حریم خصوصی افراد و قوانین حقوق مؤلف (کپی‌رایت) صورت گیرد. <b>کاربر نهایی</b> تنها شخص پاسخگو در قبال محتوای استخراج شده است.</li>
                <li><b>سلب مسئولیت مطلق:</b> توسعه‌دهنده نرم‌افزار، اساتید محترم راهنما و دانشگاه مربوطه، هیچ‌گونه مسئولیت مدنی، کیفری یا اخلاقی در قبال سوءاستفاده‌های احتمالی از این ابزار و نقض قوانین سایبری را نمی‌پذیرند.</li>
                <li><b>متن‌باز (Open-Source):</b> این ابزار یک پروژه متن‌باز است. هرگونه توزیع مجدد آن باید با حفظ نام توسعه‌دهنده اصلی و بدون رویکرد درآمدزایی انجام شود.</li>
            </ul>
            <hr style='border: 1px solid #313244; margin: 15px 0;'>
            <h3 style='color: #A6E3A1; margin-bottom: 5px; font-family: Tahoma; font-size: 13pt;'>شناسنامه پروژه آکادمیک:</h3>
            <p style='font-family: Tahoma; font-size: 12pt; line-height: 1.6; color: #A6ADC8;'>
                <b>توسعه‌دهنده:</b> مهندس ابراهیم جوهری (دانشجوی مهندسی کامپیوتر نرم‌افزار)<br>
                <b>دانشکده:</b> دانشکده آموزش عالی زرند - دانشگاه شهید باهنر کرمان<br>
                <b>پروژه درس:</b> طراحی الگوریتم (استاد محترم: دکتر علی ناصر اسدی)<br>
                <b>مدیرگروه محترم:</b> استاد دکتر علی رهنما<br>
                <b>نسخه موتور پردازشی:</b> ۵.۰ (ویرایش هوشمند)<br>
            </p>
        </div>
        """
        text.setHtml(content)
        layout.addWidget(text)
        
        chk_agree = QCheckBox("کلیه بندهای توافق‌نامه، هشدارها و سیاست‌های حقوقی فوق را با دقت خوانده و شخصاً مسئولیت آن را می‌پذیرم.")
        chk_agree.setStyleSheet("font-size: 11pt; color: #A6E3A1; font-weight: bold; margin: 10px 0; spacing: 10px;")
        layout.addWidget(chk_agree)
        
        btn_layout = QHBoxLayout()
        self.btn_accept = QPushButton("✔ موافقم؛ اجرای سیستم")
        self.btn_accept.setStyleSheet("background-color: #A6E3A1; color: #11111B;")
        self.btn_accept.setEnabled(False)
        self.btn_accept.clicked.connect(self.accept)
        
        btn_decline = QPushButton("❌ عدم تایید و خروج")
        btn_decline.setStyleSheet("background-color: #F38BA8; color: #11111B;")
        btn_decline.clicked.connect(self.reject)
        
        chk_agree.toggled.connect(self.btn_accept.setEnabled)
        btn_layout.addWidget(self.btn_accept)
        btn_layout.addWidget(btn_decline)
        layout.addLayout(btn_layout)

class DynamicSplashScreen(QSplashScreen):
    def __init__(self, pixmap, text_y_offset):
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        ico_path = os.path.join(IMG_DIR, "Ico.png")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        
        self.loading_texts = [
            "در حال بارگذاری هسته گرافیکی (PyQt6)...",
            "پیکربندی محیط ایزوله مرورگر (Playwright)...",
            "ارتباط با ماژول‌های پایگاه داده و مدیریت اکسل...",
            "در حال همگام‌سازی توابع سیستم‌عامل...",
            "بررسی مجوزها و پروتکل‌های امنیتی...",
            "آماده‌سازی پنل مدیریت پیشرفته...",
            "در حال راه‌اندازی نهایی نرم‌افزار..."
        ]
        self.step = 0
        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setGeometry(15, text_y_offset, pixmap.width() - 30, 80)
        self.update_message()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(700)
        
    def update_message(self):
        if self.step < len(self.loading_texts):
            current_text = self.loading_texts[self.step]
            html = f"<div style='background-color: rgba(22, 22, 34, 0.95); color: #A6E3A1; padding: 10px; border-radius: 8px; border: 1px solid #313244; font-family: Tahoma; font-size: 10pt; font-weight: bold; text-align: center;'>{current_text}<br><span style='color:#CDD6F4; font-size: 9pt;'>لطفاً منتظر بمانید</span></div>"
            self.text_label.setText(html)
            self.step += 1
            QCoreApplication.processEvents()

def launch_main_gui(splash):
    try:
        import main_gui
        global main_window
        # نام کلاس دقیقا با فایل main_gui سینک شد
        main_window = main_gui.ModernEitaaGUI()
        splash.finish(main_window)
        main_window.show()
    except Exception as e:
        with open("error_debug.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        ctypes.windll.user32.MessageBoxW(0, f"Error Loading GUI:\n{str(e)}", "Fatal Error", 0x10 | 0x0)
        sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    welcome = WelcomeDialog()
    if welcome.exec() == QDialog.DialogCode.Rejected:
        sys.exit(0)
        
    logo_path1 = os.path.join(IMG_DIR, "logo.png")
    logo_path2 = os.path.join(IMG_DIR, "logo-s.png")
    
    pix1 = QPixmap(logo_path1)
    pix2 = QPixmap(logo_path2)
    
    if not pix1.isNull(): pix1 = pix1.scaledToWidth(260, Qt.TransformationMode.SmoothTransformation)
    if not pix2.isNull(): pix2 = pix2.scaledToWidth(260, Qt.TransformationMode.SmoothTransformation)
    
    h1 = pix1.height() if not pix1.isNull() else 0
    h2 = pix2.height() if not pix2.isNull() else 0
    spacing = 20
    text_area_h = 100
    
    combined_w = 320
    combined_h = 20 + h1 + spacing + h2 + spacing + text_area_h + 10
    
    combined_pixmap = QPixmap(combined_w, combined_h)
    combined_pixmap.fill(QColor("#1E1E2E"))
    
    painter = QPainter(combined_pixmap)
    current_y = 20
    if not pix1.isNull():
        painter.drawPixmap((combined_w - pix1.width()) // 2, current_y, pix1)
        current_y += h1 + spacing
    if not pix2.isNull():
        painter.drawPixmap((combined_w - pix2.width()) // 2, current_y, pix2)
        current_y += h2
    painter.end()
    
    splash = DynamicSplashScreen(combined_pixmap, current_y + 15)
    splash.show()
    app.processEvents()
    
    QTimer.singleShot(6000, lambda: launch_main_gui(splash))
    sys.exit(app.exec())