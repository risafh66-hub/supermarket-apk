import sqlite3
from datetime import datetime
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp

# --- نفس قاعدة البيانات والمنطق تبعك 100% ---
conn=sqlite3.connect("supermarket.db")
cur=conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS purchases (code TEXT, name TEXT, qty REAL, price REAL, sell_price REAL, date TEXT, total REAL, remain_qty REAL)")
cur.execute("CREATE TABLE IF NOT EXISTS sales (code TEXT, name TEXT, qty REAL, price REAL, date TEXT, total REAL, buy_price REAL)")
cur.execute("CREATE TABLE IF NOT EXISTS debts (name TEXT, amount REAL, paid REAL, date TEXT, remain REAL)")
cur.execute("CREATE TABLE IF NOT EXISTS expenses (bayan TEXT, amount REAL, date TEXT, day TEXT)")
conn.commit()

def to_en(s): return str(s).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩","0123456789")).strip()
def fmt(n):
    try: v=float(to_en(n) or 0); return f"{int(v)}" if v==int(v) else f"{v:.2f}".rstrip('0').rstrip('.')
    except: return "0"
def get_date(): return datetime.now().strftime("%d/%m/%Y")
ARABIC_DAYS={"Monday":"الإثنين","Tuesday":"الثلاثاء","Wednesday":"الأربعاء","Thursday":"الخميس","Friday":"الجمعة","Saturday":"السبت","Sunday":"الأحد"}
def get_day(): return ARABIC_DAYS.get(datetime.now().strftime("%A"), "")
def get_name(code):
    r=cur.execute("SELECT name FROM purchases WHERE code=? ORDER BY rowid DESC LIMIT 1",(to_en(code),)).fetchone()
    return to_en(r[0]) if r and r[0]!="-" else ""
def get_stock(code): return float(cur.execute("SELECT SUM(remain_qty) FROM purchases WHERE code=?",(to_en(code),)).fetchone()[0] or 0)
def get_sell_price(code):
    r=cur.execute("SELECT sell_price FROM purchases WHERE code=? AND remain_qty>0 ORDER BY rowid ASC LIMIT 1",(to_en(code),)).fetchone()
    if r: return float(to_en(r[0]) or 0)
    r=cur.execute("SELECT sell_price FROM purchases WHERE code=? ORDER BY rowid DESC LIMIT 1",(to_en(code),)).fetchone()
    return float(to_en(r[0]) or 0) if r else 0

KV = '''
MDScreenManager:
    MainScreen:
    SalesScreen:
    PurchasesScreen:
    ExpensesScreen:
    DebtsScreen:
    ZakatScreen:
    StockScreen:

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#2C3E50"
        spacing: dp(10)
        padding: dp(15)
        MDLabel:
            text: "نظام سوبرماركت - الحلة الجديدة"
            halign: "center"
            bold: True
            theme_text_color: "Custom"
            text_color: 1,1,1,1
            font_style: "H5"
            size_hint_y: 0.25
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(12)
            MDRaisedButton:
                text: "مبيعات"
                md_bg_color: "#1E6F5C"
                size_hint_x: 1
                on_release: app.root.current = "sales"
            MDRaisedButton:
                text: "مشتريات"
                md_bg_color: "#34495E"
                size_hint_x: 1
                on_release: app.root.current = "purchases"
            MDRaisedButton:
                text: "مصاريف"
                md_bg_color: "#6C3483"
                size_hint_x: 1
                on_release: app.root.current = "expenses"
            MDRaisedButton:
                text: "ديون"
                md_bg_color: "#7D5A29"
                size_hint_x: 1
                on_release: app.root.current = "debts"
            MDRaisedButton:
                text: "المخزن"
                md_bg_color: "#2C3E50"
                size_hint_x: 1
                on_release: app.root.current = "stock"
            MDRaisedButton:
                text: "الزكاة الحقيقية"
                md_bg_color: "#1A5276"
                size_hint_x: 1
                on_release: app.root.current = "zakat"

<SalesScreen>:
    name: "sales"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#E8F8F5"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#1E6F5C"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "مبيعات"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(10)
            spacing: dp(8)
            size_hint_y: None
            height: dp(260)
            MDTextField:
                id: code_field
                hint_text: "الرقم - كود الصنف"
                helper_text: "ادخل كود الصنف"
                on_text: root.auto_fill()
            MDTextField:
                id: name_field
                hint_text: "الصنف"
            MDTextField:
                id: qty_field
                hint_text: "العدد"
                input_filter: "float"
            MDLabel:
                id: stock_label
                text: "المتبقي: -"
                halign: "center"
                theme_text_color: "Custom"
                text_color: "#7D6608"
            MDRaisedButton:
                text: "بيع"
                md_bg_color: "#1E6F5C"
                size_hint_x: 1
                on_release: root.do_sale()
        ScrollView:
            MDLabel:
                id: table_label
                text: "المبيعات ستظهر هنا"
                halign: "center"

<PurchasesScreen>:
    name: "purchases"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#EBEDEF"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#34495E"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "مشتريات"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(10)
            spacing: dp(8)
            MDTextField:
                id: p_code
                hint_text: "الرقم"
            MDTextField:
                id: p_name
                hint_text: "الصنف"
            MDTextField:
                id: p_qty
                hint_text: "الكمية"
                input_filter: "float"
            MDTextField:
                id: p_price
                hint_text: "سعر الشراء"
                input_filter: "float"
            MDTextField:
                id: p_sell
                hint_text: "سعر البيع"
                input_filter: "float"
            MDRaisedButton:
                text: "اضافة للمخزن"
                md_bg_color: "#34495E"
                size_hint_x: 1
                on_release: root.do_purchase()
            MDLabel:
                id: p_result
                text: ""
                halign: "center"

<ExpensesScreen>:
    name: "expenses"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#F4ECF7"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#6C3483"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "مصاريف"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(10)
            spacing: dp(8)
            MDTextField:
                id: e_bayan
                hint_text: "البيان"
            MDTextField:
                id: e_amount
                hint_text: "المبلغ"
                input_filter: "float"
            MDRaisedButton:
                text: "اضافة مصروف"
                md_bg_color: "#6C3483"
                size_hint_x: 1
                on_release: root.do_expense()
            MDLabel:
                id: e_result
                text: ""
                halign: "center"

<DebtsScreen>:
    name: "debts"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#F5EBE0"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#7D5A29"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "ديون"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(10)
            spacing: dp(8)
            MDTextField:
                id: d_name
                hint_text: "الاسم"
            MDTextField:
                id: d_amount
                hint_text: "المبلغ"
                input_filter: "float"
            MDTextField:
                id: d_paid
                hint_text: "دفعة"
                input_filter: "float"
            MDRaisedButton:
                text: "اضافة دين"
                md_bg_color: "#7D5A29"
                size_hint_x: 1
                on_release: root.do_debt()

<ZakatScreen>:
    name: "zakat"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: "#FEF9E7"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#1A5276"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "الزكاة الحقيقية"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        MDLabel:
            id: result_label
            text: "جاري الحساب..."
            halign: "center"
            font_style: "H6"

<StockScreen>:
    name: "stock"
    MDBoxLayout:
        orientation: "vertical"
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: "#2C3E50"
            MDFlatButton:
                text: "رجوع"
                theme_text_color: "Custom"
                text_color: 1,1,1,1
                on_release: app.root.current = "main"
            MDLabel:
                text: "المخزن"
                halign: "center"
                bold: True
                theme_text_color: "Custom"
                text_color: 1,1,1,1
        ScrollView:
            MDLabel:
                id: stock_table
                text: ""
                halign: "center"
'''

class MainScreen(MDScreen): pass

class SalesScreen(MDScreen):
    def auto_fill(self):
        code = to_en(self.ids.code_field.text)
        if code:
            self.ids.name_field.text = get_name(code)
            self.ids.stock_label.text = f"المتبقي: {fmt(get_stock(code))} - سعر البيع: {fmt(get_sell_price(code))}"
    def do_sale(self):
        code = to_en(self.ids.code_field.text)
        qty = float(to_en(self.ids.qty_field.text) or 0)
        if not code or qty==0: return
        if qty > get_stock(code):
            self.ids.stock_label.text = f"خطأ: المتبقي {fmt(get_stock(code))} فقط!"
            return
        name = to_en(self.ids.name_field.text) or get_name(code) or "-"
        remaining=qty
        for pid, remain, buy, sell in cur.execute("SELECT rowid, remain_qty, price, sell_price FROM purchases WHERE code=? AND remain_qty>0 ORDER BY rowid ASC",(code,)).fetchall():
            if remaining<=0: break
            take=min(remaining, float(remain or 0))
            cur.execute("UPDATE purchases SET remain_qty=? WHERE rowid=?", (float(remain)-take, pid))
            cur.execute("INSERT INTO sales VALUES (?,?,?,?,?,?,?)",(code, name, take, float(sell), get_date(), take*float(sell), buy))
            remaining-=take
        conn.commit()
        self.ids.qty_field.text=""
        self.ids.stock_label.text = f"تم البيع - المتبقي: {fmt(get_stock(code))}"
        self.ids.table_label.text = f"آخر بيع: {name} - {fmt(qty)} - {fmt(qty*get_sell_price(code))}"

class PurchasesScreen(MDScreen):
    def do_purchase(self):
        code=to_en(self.ids.p_code.text); name=to_en(self.ids.p_name.text) or "-"
        qty=float(to_en(self.ids.p_qty.text) or 0); price=float(to_en(self.ids.p_price.text) or 0); sell=float(to_en(self.ids.p_sell.text) or 0)
        if not code or qty==0: return
        cur.execute("INSERT INTO purchases VALUES (?,?,?,?,?,?,?,?)",(code, name, qty, price, sell, get_date(), qty*price, qty))
        conn.commit()
        self.ids.p_result.text = f"تمت الاضافة: {name} - {fmt(qty)}"
        for k in ['p_code','p_name','p_qty','p_price','p_sell']: self.ids[k].text=""

class ExpensesScreen(MDScreen):
    def do_expense(self):
        bayan=to_en(self.ids.e_bayan.text); amount=float(to_en(self.ids.e_amount.text) or 0)
        if not bayan or amount==0: return
        cur.execute("INSERT INTO expenses VALUES (?,?,?,?)",(bayan, amount, get_date(), get_day()))
        conn.commit()
        self.ids.e_result.text = f"تم: {bayan} - {fmt(amount)}"
        self.ids.e_bayan.text=""; self.ids.e_amount.text=""

class DebtsScreen(MDScreen):
    def do_debt(self):
        name=to_en(self.ids.d_name.text); amount=float(to_en(self.ids.d_amount.text) or 0); paid=float(to_en(self.ids.d_paid.text) or 0)
        if not name or amount==0: return
        cur.execute("INSERT INTO debts VALUES (?,?,?,?,?)",(name, amount, paid, get_date(), amount-paid))
        conn.commit()
        self.ids.d_name.text=""; self.ids.d_amount.text=""; self.ids.d_paid.text=""

class ZakatScreen(MDScreen):
    def on_enter(self):
        stock_val=cur.execute("SELECT SUM(remain_qty * price) FROM purchases").fetchone()[0] or 0
        sales_val=cur.execute("SELECT SUM(total) FROM sales").fetchone()[0] or 0
        debts_val=cur.execute("SELECT SUM(amount)-SUM(paid) FROM debts").fetchone()[0] or 0
        expenses_val=cur.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0
        base=stock_val+sales_val-debts_val-expenses_val
        if base<0: base=0
        zakat=base*0.025
        self.ids.result_label.text = f"المخزن: {fmt(stock_val)}\\nالمبيعات: {fmt(sales_val)}\\n- الديون: {fmt(debts_val)}\\n- المصاريف: {fmt(expenses_val)}\\n\\nالوعاء: {fmt(base)}\\nالزكاة 2.5%: {fmt(zakat)}"

class StockScreen(MDScreen):
    def on_enter(self):
        txt=""
        for code,name,pur,rem in cur.execute("SELECT code, MAX(name), SUM(qty), SUM(remain_qty) FROM purchases GROUP BY code"):
            txt+=f"{to_en(code)} - {to_en(name)} | مشترى: {fmt(pur)} - متبقي: {fmt(rem)}\\n"
        self.ids.stock_table.text = txt or "المخزن فارغ"

class SupermarketApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_string(KV)

SupermarketApp().run()