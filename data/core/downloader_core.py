# data/core/downloader_core.py
import sys, os, re, time, queue, threading
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from PyQt6.QtCore import QObject, pyqtSignal

# شناسایی مسیر اصلی نرم‌افزار (دو پوشه بالاتر از core)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "Eitaa_PDFs")

class EitaaWorkerThread(QObject):
    log_signal           = pyqtSignal(str, str)
    finished_signal      = pyqtSignal(str, int)
    progress_signal      = pyqtSignal(int, int)
    browser_ready_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.browser_opened  = False
        self._stop_flag      = False

        self.download_folder = DOWNLOAD_FOLDER
        self.keyword_filter  = ""
        self.headless_mode   = False
        self.skip_duplicates = True
        self.quick_mode      = False
        self.scroll_count    = 5
        self.max_files       = 0
        self.timeout_sec     = 180
        self.retry_count     = 2
        self.scroll_delay    = 2
        
        self.export_link   = True
        self.export_size   = True
        self.export_date   = True
        self.export_status = True

        self._browser = None
        self._page    = None
        self._context = None
        self._pw      = None

        self._task_queue = queue.Queue()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    @property
    def excel_path(self):
        return os.path.join(self.download_folder, "Downloaded_PDFs_Report.xlsx")

    def open_browser(self): 
        self._task_queue.put(("open_browser", {}))
        
    def start_scan_and_download(self): 
        self._stop_flag = False
        self._task_queue.put(("scan", {}))
        
    def stop_process(self):
        self._stop_flag = True
        self.log("دستور توقف صادر شد. لطفاً کمی صبر کنید...", "warning")

    def _loop(self):
        while True:
            try:   task, _ = self._task_queue.get(timeout=0.5)
            except queue.Empty: continue
            if   task == "open_browser": self._do_open_browser()
            elif task == "scan":         self._do_scan()

    def log(self, txt, kind="info"):
        self.log_signal.emit(f"[{datetime.now():%H:%M:%S}] {txt}", kind)

    def _build_row(self, short, dname, fsize, dest, status):
        row = {"نام فایل": short}
        
        if self.export_link and dest and dest != "—":
            abs_dest = os.path.abspath(dest).replace('\\', '/')
            abs_dir = os.path.dirname(abs_dest)
            row["فایل نهایی (لینک)"] = f'=HYPERLINK("file:///{abs_dest}", "{dname}")'
            row["پوشه"] = f'=HYPERLINK("file:///{abs_dir}", "نمایش در پوشه")'
        else:
            row["فایل نهایی (لینک)"] = dname
            row["پوشه"] = "—" if self.export_link else (dest if dest else "—")

        if self.export_size:   row["حجم"] = fsize if fsize else "?"
        if self.export_date:   row["تاریخ ثبت"] = datetime.now().strftime("%Y/%m/%d %H:%M")
        if self.export_status: row["وضعیت"] = status
            
        return row

    def _is_duplicate(self, clean_name):
        if self.skip_duplicates and os.path.exists(self.excel_path):
            try:
                df = pd.read_excel(self.excel_path, engine='openpyxl')
                if 'نام فایل' in df.columns:
                    for _, row in df.iterrows():
                        if clean_name in str(row['نام فایل']) and 'موفق' in str(row.get('وضعیت', '')):
                            return True
            except: pass
        return False

    def _do_open_browser(self):
        if self.browser_opened:
            self.log("مرورگر از قبل در حال اجراست.", "warning")
            return
        os.makedirs(self.download_folder, exist_ok=True)
        try:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(
                headless=self.headless_mode, 
                args=['--disable-blink-features=AutomationControlled']
            )
            self._context = self._browser.new_context(accept_downloads=True)
            self._page    = self._context.new_page()
            self._page.goto("https://web.eitaa.com/")
            
            self.browser_opened = True
            self.log("مرورگر با موفقیت اجرا شد.", "success")
            self.browser_ready_signal.emit(True)
        except Exception as e:
            self.log(f"خطا در اجرای مرورگر: {e}", "error")
            self.browser_ready_signal.emit(False)

    def _do_scan(self):
        if not self.browser_opened or not self._page:
            self.log("ابتدا مرورگر را اجرا کنید.", "error")
            self.finished_signal.emit("error", 0)
            return

        os.makedirs(self.download_folder, exist_ok=True)
        page = self._page
        report_data = []

        if os.path.exists(self.excel_path):
            try: report_data = pd.read_excel(self.excel_path, engine='openpyxl').to_dict('records')
            except: pass

        self.log(f"در حال بارگذاری پیام‌های قدیمی ({self.scroll_count} صفحه)...", "info")
        for _ in range(self.scroll_count):
            if self._stop_flag: break
            page.mouse.wheel(0, -5000)
            time.sleep(self.scroll_delay)

        self.log("در حال بررسی فایل‌های PDF...", "info")
        document_elements = page.locator(".document").all()
        
        if not document_elements:
            self.log("هیچ فایلی در این کانال یافت نشد.", "error")
            self.finished_signal.emit("empty", 0)
            return

        downloaded_count = 0
        total_found = len(document_elements)
        
        if self.max_files > 0 and total_found > self.max_files:
            document_elements = document_elements[-self.max_files:]
            total_found = len(document_elements)

        self.log(f"تعداد {total_found} فایل در صفحه پیدا شد.", "success")

        for idx, element in enumerate(document_elements):
            if self._stop_flag:
                self.log("عملیات توسط کاربر متوقف شد.", "warning")
                break
                
            self.progress_signal.emit(idx + 1, total_found)

            try:
                text_content = element.inner_text(timeout=2000).lower()
                if ".pdf" in text_content:
                    lines = text_content.split('\n')
                    file_name = next((line for line in lines if ".pdf" in line), f"document_{idx}.pdf")
                    clean_file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name.strip())
                    
                    if self.keyword_filter and self.keyword_filter.lower() not in clean_file_name.lower():
                        continue

                    fsize = "?"
                    for line in lines:
                        if any(u in line.upper() for u in ['KB','MB',' B','GB']):
                            fsize = line.strip()
                            break

                    if self._is_duplicate(clean_file_name):
                        self.log(f"فایل تکراری است (رد شد): {clean_file_name[:30]}", "warning")
                        continue

                    if self.quick_mode:
                        report_data.append(self._build_row(clean_file_name, "—", fsize, "—", "ثبت در لیست ✓"))
                        continue

                    self.log(f"پردازش: {clean_file_name[:40]}", "info")
                    
                    while len(self._context.pages) > 1:
                        self._context.pages[-1].close()
                        time.sleep(0.5)
                    
                    page.mouse.click(10, 10)
                    page.keyboard.press("Escape")
                    time.sleep(0.5)

                    element.scroll_into_view_if_needed()
                    time.sleep(1)

                    box = element.bounding_box()
                    if not box: continue

                    center_x, center_y = box["x"] + (box["width"] / 2), box["y"] + (box["height"] / 2)

                    success = False
                    for attempt in range(self.retry_count):
                        try:
                            page.mouse.click(center_x, center_y, button="right")
                            dl_option = page.get_by_text("دانلود", exact=True).locator("visible=true").last
                            dl_option.wait_for(state="visible", timeout=3000)
                            
                            dl_box = dl_option.bounding_box()
                            if not dl_box: continue
                            dl_center_x, dl_center_y = dl_box["x"] + (dl_box["width"] / 2), dl_box["y"] + (dl_box["height"] / 2)

                            with page.expect_download(timeout=self.timeout_sec * 1000) as dl_info:
                                page.mouse.click(dl_center_x, dl_center_y, button="left")
                                
                            download = dl_info.value
                            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                            safe_name = f"{timestamp}_{clean_file_name}"
                            save_path = os.path.join(self.download_folder, safe_name)
                            
                            download.save_as(save_path)
                            self.log(f"دانلود موفق: {safe_name[:40]}", "success")
                            downloaded_count += 1
                            report_data.append(self._build_row(clean_file_name, safe_name, fsize, save_path, "موفق ✓"))
                            success = True
                            break
                            
                        except PWTimeout:
                            page.keyboard.press("Escape")
                            if attempt < self.retry_count - 1:
                                self.log("تلاش مجدد برای دانلود...", "warning")
                                time.sleep(2)
                        except Exception as e:
                            page.keyboard.press("Escape")
                            break
                            
                    if not success:
                        self.log("شکست در دریافت فایل.", "error")
                        report_data.append(self._build_row(clean_file_name, "—", fsize, "—", "خطا ❌"))
                        
            except Exception as e: pass

        if report_data:
            df = pd.DataFrame(report_data)
            df.to_excel(self.excel_path, index=False, engine='openpyxl')

        status = "success" if downloaded_count > 0 or self.quick_mode else "empty"
        if self._stop_flag: status = "stopped"
        self.finished_signal.emit(status, downloaded_count)