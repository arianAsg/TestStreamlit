import streamlit as st
import pandas as pd
from datetime import datetime
import os
import jdatetime

# تنظیمات اولیه
st.set_page_config(page_title="مدیریت حساب‌های بانکی", layout="wide")

# نام فایل‌ها و دایرکتوری‌ها
banks_file = "banks.xlsx"
transactions_file = "transactions.xlsx"
receipts_dir = "receipts"

# توابع کمکی
def format_currency(amount):
    """فرمت کردن مبلغ با کاما برای نمایش"""
    try:
        return "{:,.0f}".format(float(amount))
    except:
        return amount

def parse_currency(amount_str):
    """تبدیل مبلغ فرمت شده به عدد برای ذخیره"""
    try:
        return float(str(amount_str).replace(",", "").strip())
    except:
        return 0.0

def convert_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    try:
        if isinstance(gregorian_date, str):
            gregorian_date = datetime.strptime(gregorian_date, "%Y/%m/%d")
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return jalali_date.strftime("%Y/%m/%d")
    except:
        return gregorian_date

def load_data():
    """بارگذاری داده‌ها از فایل‌های اکسل"""
    if os.path.exists(banks_file):
        df_banks = pd.read_excel(banks_file)
    else:
        df_banks = pd.DataFrame(columns=["Bank Name", "Balance"])

    if os.path.exists(transactions_file):
        df_transactions = pd.read_excel(transactions_file)
    else:
        df_transactions = pd.DataFrame(columns=["Bank Name", "Transaction Type", "Amount", "Date", "Purpose", "Person", "Receipt"])
    
    return df_banks, df_transactions

def save_data(df_banks, df_transactions):
    """ذخیره داده‌ها در فایل‌های اکسل"""
    df_banks.to_excel(banks_file, index=False)
    df_transactions.to_excel(transactions_file, index=False)

# بارگذاری داده‌ها
df_banks, df_transactions = load_data()

# ⬇ انتخاب منو
menu = st.sidebar.selectbox("منو", [
    "ایجاد حساب",
    "لیست حساب‌ها",
    "تراکنش جدید",
    "نمایش تمام تراکنش‌ها",
    "تراکنش‌های واریزی",
    "تراکنش‌های برداشتی"
])

# ---------------------
# 🏦 ایجاد حساب جدید
# ---------------------
if menu == "ایجاد حساب":
    st.header("ایجاد حساب بانکی جدید")
    
    col1, col2 = st.columns(2)
    with col1:
        bank_name = st.text_input("نام بانک")
    with col2:
        amount = st.text_input("مبلغ اولیه", value="0", key="initial_amount")

    # نمایش پیش‌نمایش مبلغ
    if amount:
        try:
            cleaned_amount = amount.replace(",", "").replace(" ", "")
            if cleaned_amount:  # فقط اگر مقدار خالی نباشد
                formatted_amount = format_currency(cleaned_amount)
                st.caption(f"مبلغ به عدد: {formatted_amount}")
        except:
            pass

    if st.button("ایجاد حساب", type="primary"):
        try:
            # اعتبارسنجی نام بانک
            if not bank_name or not bank_name.strip():
                st.error("لطفاً نام بانک را وارد کنید.")
                
                
            # پردازش و اعتبارسنجی مبلغ
            cleaned_amount = amount.replace(",", "").replace(" ", "").strip()
            
            if not cleaned_amount:  # اگر مقدار خالی باشد
                st.error("لطفاً مبلغ را وارد کنید.")
                
                
            try:
                initial_amount = float(cleaned_amount)
            except ValueError:
                st.error("لطفاً یک عدد معتبر وارد کنید (مثال: 1000000 یا 1,000,000)")
                
                
            if initial_amount < 0:
                st.error("مبلغ نمی‌تواند منفی باشد.")
                
                
            # بررسی تکراری نبودن نام بانک
            if bank_name in df_banks["Bank Name"].values:
                st.warning("این بانک قبلاً ثبت شده است.")
                
                
            # ایجاد حساب جدید
            df_banks.loc[len(df_banks)] = [bank_name, initial_amount]
            save_data(df_banks, df_transactions)
            
            st.success(f"""
            ✅ حساب بانکی با موفقیت ایجاد شد:
            - نام بانک: {bank_name}
            - موجودی اولیه: {format_currency(initial_amount)} ریال
            """)
            
        except Exception as e:
            st.error(f"خطای غیرمنتظره: {str(e)}")

# ---------------------
# 📄 لیست حساب‌ها
# ---------------------
elif menu == "لیست حساب‌ها":
    st.header("لیست حساب‌های موجود")
    
    if df_banks.empty:
        st.info("هیچ حسابی موجود نیست.")
    else:
        # تغییر نام ستون‌ها به فارسی
        display_df = df_banks.copy()
        display_df.columns = ["نام بانک", "موجودی"]
        
        # فرمت کردن موجودی با کاما
        display_df["موجودی"] = display_df["موجودی"].apply(format_currency)
        
        # محاسبه جمع کل موجودی‌ها
        total_balance = df_banks["Balance"].sum()
        
        # استفاده از st.dataframe برای نمایش زیباتر
        st.dataframe(
            display_df,
            column_config={
                "نام بانک": st.column_config.TextColumn("نام بانک", width="medium"),
                "موجودی": st.column_config.TextColumn("موجودی (ریال)", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown(f"**جمع کل موجودی‌ها:** {format_currency(total_balance)} ریال")

# ---------------------
# 💸 تراکنش جدید
# ---------------------
elif menu == "تراکنش جدید":
    st.header("ثبت تراکنش")

    if df_banks.empty:
        st.warning("هیچ بانکی وجود ندارد. ابتدا یک حساب ایجاد کنید.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_bank = st.selectbox("انتخاب بانک", df_banks["Bank Name"].tolist())
            transaction_type = st.radio("نوع تراکنش", ["واریز", "برداشت"])
            amount = st.text_input("مبلغ", value="0", key="amount_input")
            
            if amount:
                try:
                    formatted_amount = format_currency(amount.replace(",", ""))
                    st.caption(f"مبلغ به عدد: {formatted_amount}")
                except:
                    pass
                
        with col2:
            purpose = st.text_input("علت تراکنش")
            person = st.text_input("شخص / شرکت")
            date_choice = st.radio("تاریخ", ["تاریخ امروز", "ورود دستی"])
            
            if date_choice == "ورود دستی":
                date_input = st.text_input("تاریخ (YYYY/MM/DD)")
                try:
                    date = convert_to_jalali(date_input)
                except:
                    date = date_input
            else:
                today = datetime.today()
                date = convert_to_jalali(today)
                st.caption(f"تاریخ امروز: {date}")

        receipt = st.file_uploader("آپلود تصویر رسید (اختیاری)", type=["jpg", "png", "jpeg"])

        if st.button("ثبت تراکنش", type="primary"):
            try:
                transaction_amount = parse_currency(amount)
                if transaction_amount <= 0:
                    st.error("مبلغ باید بزرگتر از صفر باشد.")
                    
                    
                current_balance = df_banks.loc[df_banks['Bank Name'] == selected_bank, 'Balance'].values[0]
                
                if transaction_type == "واریز":
                    new_balance = current_balance + transaction_amount
                else:
                    new_balance = current_balance - transaction_amount
                    if new_balance < 0:
                        st.error("موجودی کافی نیست.")
                        

                # به‌روزرسانی موجودی بانک
                df_banks.loc[df_banks["Bank Name"] == selected_bank, "Balance"] = new_balance

                # ذخیره تصویر رسید
                receipt_path = ""
                if receipt is not None:
                    os.makedirs(receipts_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    receipt_ext = os.path.splitext(receipt.name)[1]
                    receipt_path = os.path.join(receipts_dir, f"{selected_bank}_{person}_{timestamp}{receipt_ext}")
                    with open(receipt_path, "wb") as f:
                        f.write(receipt.getbuffer())

                # ثبت تراکنش جدید
                new_transaction = pd.DataFrame([[selected_bank, transaction_type, transaction_amount, date, purpose, person, receipt_path]],
                                           columns=["Bank Name", "Transaction Type", "Amount", "Date", "Purpose", "Person", "Receipt"])
                df_transactions = pd.concat([df_transactions, new_transaction], ignore_index=True)
                
                # ذخیره تمام تغییرات
                save_data(df_banks, df_transactions)

                st.success(f"""
                تراکنش با موفقیت ثبت شد.
                - موجودی قبلی: {format_currency(current_balance)} ریال
                - موجودی جدید: {format_currency(new_balance)} ریال
                """)
            except ValueError as e:
                st.error(f"خطا در ثبت تراکنش: {str(e)}")

# ---------------------
# 📊 نمایش تراکنش‌ها
# ---------------------
elif menu in ["نمایش تمام تراکنش‌ها", "تراکنش‌های واریزی", "تراکنش‌های برداشتی"]:
    st.header(menu)
    
    if os.path.exists(transactions_file):
        df = pd.read_excel(transactions_file)
        
        # فیلتر بر اساس نوع تراکنش
        if menu == "تراکنش‌های واریزی":
            df = df[df["Transaction Type"] == "واریز"]
            total = df["Amount"].sum()
        elif menu == "تراکنش‌های برداشتی":
            df = df[df["Transaction Type"] == "برداشت"]
            total = df["Amount"].sum()
        else:
            total_income = df[df["Transaction Type"] == "واریز"]["Amount"].sum()
            total_expense = df[df["Transaction Type"] == "برداشت"]["Amount"].sum()
            total = total_income - total_expense
        
        if df.empty:
            st.info("تراکنشی یافت نشد.")
        else:
            # تغییر نام ستون‌ها به فارسی
            display_df = df.copy()
            display_df.columns = ["نام بانک", "نوع تراکنش", "مبلغ", "تاریخ", "علت", "شخص/شرکت", "رسید"]
            
            # فرمت کردن مبلغ
            display_df["مبلغ"] = display_df["مبلغ"].apply(format_currency)
            
            # نمایش جدول
            st.dataframe(
                display_df,
                column_config={
                    "نام بانک": st.column_config.TextColumn(width="medium"),
                    "نوع تراکنش": st.column_config.TextColumn(width="small"),
                    "مبلغ": st.column_config.TextColumn("مبلغ (ریال)", width="medium"),
                    "تاریخ": st.column_config.DateColumn("تاریخ", format="YYYY/MM/DD"),
                    "علت": st.column_config.TextColumn(width="large"),
                    "شخص/شرکت": st.column_config.TextColumn(width="medium"),
                    "رسید": st.column_config.LinkColumn("رسید")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # نمایش جمع کل
            if menu == "تراکنش‌های واریزی":
                st.markdown(f"**جمع کل واریزها:** {format_currency(total)} ریال")
            elif menu == "تراکنش‌های برداشتی":
                st.markdown(f"**جمع کل برداشت‌ها:** {format_currency(total)} ریال")
            else:
                st.markdown(f"""
                - **جمع کل واریزها:** {format_currency(total_income)} ریال
                - **جمع کل برداشت‌ها:** {format_currency(total_expense)} ریال
                - **مانده کل:** {format_currency(total)} ریال
                """)
    else:
        st.info("تراکنشی یافت نشد.")

# راهنمای نصب
st.sidebar.markdown("""
### راهنمای نصب
1. نصب کتابخانه‌های مورد نیاز:""")