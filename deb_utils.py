import streamlit as st
import pandas as pd
from datetime import datetime
import os
import jdatetime
from PIL import Image
import io

debts_file = "debts.xlsx"
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

def load_debts_data():
    """بارگذاری داده‌های طلبکاران/بدهکاران"""
    if os.path.exists(debts_file):
        df_debts = pd.read_excel(debts_file)
    else:
        df_debts = pd.DataFrame(columns=[
            "Type", "Name", "Amount", "Description", 
            "Due Date", "Contact", "Registered Date"
        ])
    return df_debts

def save_debts_data(df_debts):
    """ذخیره داده‌های طلبکاران/بدهکاران"""
    df_debts.to_excel(debts_file, index=False)

def register_debt(debt_type, name, amount, description, due_date, contact):
    """ثبت طلبکار/بدهکار جدید"""
    try:
        df_debts = load_debts_data()
        
        # تبدیل تاریخ به میلادی برای ذخیره سازی
        gregorian_due_date = convert_to_gregorian(due_date)
        current_date = convert_to_jalali(datetime.now().strftime("%Y/%m/%d"))
        gregorian_registered_date = convert_to_gregorian(current_date)
        
        # ثبت رکورد جدید
        new_debt = pd.DataFrame([[
            debt_type, name, amount, description,
            gregorian_due_date, contact, gregorian_registered_date
        ]], columns=[
            "Type", "Name", "Amount", "Description", 
            "Due Date", "Contact", "Registered Date"
        ])
        
        df_debts = pd.concat([df_debts, new_debt], ignore_index=True)
        save_debts_data(df_debts)
        
        return True, current_date
    except Exception as e:
        return False, str(e)

def delete_debt(index):
    """حذف طلبکار/بدهکار"""
    try:
        df_debts = load_debts_data()
        if 0 <= index < len(df_debts):
            df_debts = df_debts.drop(index).reset_index(drop=True)
            save_debts_data(df_debts)
            return True
        return False
    except Exception as e:
        st.error(f"خطا در حذف رکورد: {str(e)}")
        return False

def display_debts():
    """نمایش لیست طلبکاران/بدهکاران"""
    df_debts = load_debts_data()
    
    if df_debts.empty:
        st.info("هیچ رکوردی ثبت نشده است.")
        return
    
    # تبدیل تاریخ‌ها به شمسی برای نمایش
    display_df = df_debts.copy()
    display_df["Due Date"] = display_df["Due Date"].apply(convert_to_jalali)
    display_df["Registered Date"] = display_df["Registered Date"].apply(convert_to_jalali)
    
    # تغییر نام ستون‌ها به فارسی
    display_df.columns = [
        "نوع", "نام", "مبلغ", "توضیحات", 
        "تاریخ وصول", "اطلاعات تماس", "تاریخ ثبت"
    ]
    
    # فرمت کردن مبلغ
    display_df["مبلغ"] = display_df["مبلغ"].apply(format_currency)
    
    # نمایش جدول با امکان حذف
    for i in range(len(display_df)):
        cols = st.columns([5, 5, 3, 3, 3, 3, 3, 1])
        with cols[0]:
            st.text(display_df.loc[i, "نوع"])
        with cols[1]:
            st.text(display_df.loc[i, "نام"])
        with cols[2]:
            st.text(display_df.loc[i, "مبلغ"])
        with cols[3]:
            st.text(display_df.loc[i, "توضیحات"])
        with cols[4]:
            st.text(display_df.loc[i, "تاریخ وصول"])
        with cols[5]:
            st.text(display_df.loc[i, "اطلاعات تماس"])
        with cols[6]:
            st.text(display_df.loc[i, "تاریخ ثبت"])
        with cols[7]:
            if st.button("🗑️", key=f"del_{i}"):
                if delete_debt(i):
                    st.rerun()
    
    # محاسبه جمع مبالغ
    total_creditors = df_debts[df_debts["Type"] == "طلبکار"]["Amount"].sum()
    total_debtors = df_debts[df_debts["Type"] == "بدهکار"]["Amount"].sum()
    
    st.markdown(f"""
    **جمع کل طلبکاران:** {format_currency(total_creditors)} ریال  
    **جمع کل بدهکاران:** {format_currency(total_debtors)} ریال  
    **مانده:** {format_currency(total_creditors - total_debtors)} ریال
    """)