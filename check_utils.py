# ---------------------
# 📌 توابع مربوط به چک‌ها
# ---------------------
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import jdatetime
from PIL import Image
import io
checks_file = "checks.xlsx"
checks_dir = "checks_images"
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

def convert_to_gregorian(jalali_date_str):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        year, month, day = map(int, jalali_date_str.split('/'))
        gregorian_date = jdatetime.date(year, month, day).togregorian()
        return gregorian_date.strftime("%Y/%m/%d")
    except:
        return jalali_date_str

def save_image(uploaded_file, directory, filename):
    """ذخیره تصویر آپلود شده"""
    try:
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"خطا در ذخیره تصویر: {str(e)}")
        return None


def load_checks_data():
    """بارگذاری داده‌های چک‌ها"""
    if os.path.exists(checks_file):
        df_checks = pd.read_excel(checks_file)
    else:
        df_checks = pd.DataFrame(columns=[
            "Check Type", "Check Number", "Due Date", "Owner Name", 
            "Amount", "Description", "Account Owner", "Image Path"
        ])
    return df_checks

def save_checks_data(df_checks):
    """ذخیره داده‌های چک‌ها"""
    df_checks.to_excel(checks_file, index=False)

def register_check(check_type, check_number, due_date, owner_name, 
                  amount, description, account_owner, check_image):
    """ثبت چک جدید"""
    try:
        df_checks = load_checks_data()
        
        # ذخیره تصویر چک
        image_path = ""
        if check_image is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(check_image.name)[1]
            image_filename = f"check_{check_number}_{timestamp}{ext}"
            image_path = save_image(check_image, checks_dir, image_filename)
        
        # تبدیل تاریخ به شمسی برای نمایش
        jalali_due_date = convert_to_jalali(due_date)
        
        # تبدیل تاریخ به میلادی برای ذخیره سازی
        gregorian_due_date = convert_to_gregorian(jalali_due_date)
        
        # ثبت چک جدید
        new_check = pd.DataFrame([[
            check_type, check_number, gregorian_due_date, owner_name,
            amount, description, account_owner, image_path
        ]], columns=[
            "Check Type", "Check Number", "Due Date", "Owner Name", 
            "Amount", "Description", "Account Owner", "Image Path"
        ])
        
        df_checks = pd.concat([df_checks, new_check], ignore_index=True)
        save_checks_data(df_checks)
        
        return True, jalali_due_date
    except Exception as e:
        return False, str(e)

def display_checks():
    """نمایش لیست چک‌ها"""
    df_checks = load_checks_data()
    
    if df_checks.empty:
        st.info("هیچ چکی ثبت نشده است.")
        return
    
    # تبدیل تاریخ‌ها به شمسی برای نمایش
    display_df = df_checks.copy()
    display_df["Due Date"] = display_df["Due Date"].apply(convert_to_jalali)
    
    # تغییر نام ستون‌ها به فارسی
    display_df.columns = [
        "نوع چک", "شماره چک", "تاریخ وصول", "نام دارنده", 
        "مبلغ", "بابت", "صاحب حساب", "مسیر تصویر"
    ]
    
    # فرمت کردن مبلغ
    display_df["مبلغ"] = display_df["مبلغ"].apply(format_currency)
    
    # نمایش جدول
    st.dataframe(
        display_df,
        column_config={
            "نوع چک": st.column_config.TextColumn(width="small"),
            "شماره چک": st.column_config.TextColumn(width="small"),
            "تاریخ وصول": st.column_config.DateColumn(format="YYYY/MM/DD"),
            "نام دارنده": st.column_config.TextColumn(width="medium"),
            "مبلغ": st.column_config.TextColumn("مبلغ (ریال)"),
            "بابت": st.column_config.TextColumn(width="large"),
            "صاحب حساب": st.column_config.TextColumn(width="medium"),
            "مسیر تصویر": st.column_config.LinkColumn("تصویر چک")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # محاسبه جمع مبالغ
    total_received = df_checks[df_checks["Check Type"] == "دریافتی"]["Amount"].sum()
    total_issued = df_checks[df_checks["Check Type"] == "صادر شده"]["Amount"].sum()
    
    st.markdown(f"""
    **جمع کل چک‌های دریافتی:** {format_currency(total_received)} ریال  
    **جمع کل چک‌های صادر شده:** {format_currency(total_issued)} ریال  
    **مانده چک‌ها:** {format_currency(total_received - total_issued)} ریال
    """)