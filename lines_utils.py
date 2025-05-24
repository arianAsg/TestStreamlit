import streamlit as st
import pandas as pd
from datetime import datetime
import os
import jdatetime
import uuid

# تنظیمات اولیه


# نام فایل‌ها
phone_numbers_file = "phone_numbers.xlsx"
partners_file = "partners.xlsx"
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
# ---------------------
# 📌 توابع مدیریت شماره‌های تلفن
# ---------------------
def load_phone_numbers():
    """بارگذاری لیست شماره‌های تلفن"""
    if os.path.exists(phone_numbers_file):
        df = pd.read_excel(phone_numbers_file)
    else:
        df = pd.DataFrame(columns=[
            "ID", "Phone Number", "Price", "Description", 
            "Register Date", "Status", "Partner ID"
        ])
    return df

def save_phone_numbers(df):
    """ذخیره لیست شماره‌های تلفن"""
    df.to_excel(phone_numbers_file, index=False)

def add_phone_number(number, price, description, partner_id=None):
    """افزودن شماره تلفن جدید"""
    try:
        df = load_phone_numbers()
        new_id = str(uuid.uuid4())
        current_date = convert_to_jalali(datetime.now().strftime("%Y/%m/%d"))
        
        new_record = pd.DataFrame([[
            new_id, number, price, description,
            current_date, "موجود", partner_id
        ]], columns=[
            "ID", "Phone Number", "Price", "Description",
            "Register Date", "Status", "Partner ID"
        ])
        
        df = pd.concat([df, new_record], ignore_index=True)
        save_phone_numbers(df)
        return True
    except Exception as e:
        st.error(f"خطا در ثبت شماره: {str(e)}")
        return False

def mark_as_sold(phone_id):
    """علامت‌گذاری شماره به عنوان فروخته شده"""
    try:
        df = load_phone_numbers()
        df.loc[df["ID"] == phone_id, "Status"] = "فروخته شده"
        save_phone_numbers(df)
        return True
    except Exception as e:
        st.error(f"خطا در بروزرسانی وضعیت: {str(e)}")
        return False

def delete_phone_number(phone_id):
    """حذف شماره تلفن"""
    try:
        df = load_phone_numbers()
        df = df[df["ID"] != phone_id]
        save_phone_numbers(df)
        return True
    except Exception as e:
        st.error(f"خطا در حذف شماره: {str(e)}")
        return False

# ---------------------
# 📌 توابع مدیریت شرکا
# ---------------------
def load_partners():
    """بارگذاری لیست شرکا"""
    if os.path.exists(partners_file):
        df = pd.read_excel(partners_file)
    else:
        df = pd.DataFrame(columns=[
            "ID", "Name", "Phone", "Address", "Register Date"
        ])
    return df

def save_partners(df):
    """ذخیره لیست شرکا"""
    df.to_excel(partners_file, index=False)

def add_partner(name, phone, address):
    """افزودن شریک جدید"""
    try:
        df = load_partners()
        new_id = str(uuid.uuid4())
        current_date = convert_to_jalali(datetime.now().strftime("%Y/%m/%d"))
        
        new_record = pd.DataFrame([[
            new_id, name, phone, address, current_date
        ]], columns=[
            "ID", "Name", "Phone", "Address", "Register Date"
        ])
        
        df = pd.concat([df, new_record], ignore_index=True)
        save_partners(df)
        return True, new_id
    except Exception as e:
        st.error(f"خطا در ثبت شریک: {str(e)}")
        return False, None

# ---------------------
# 🖥️ رابط کاربری
# ---------------------
def phone_numbers_management():
    """مدیریت شماره‌های تلفن"""
    st.header("مدیریت شماره‌های تلفن")
    
    tab1, tab2, tab3 = st.tabs(["ثبت شماره جدید", "لیست شماره‌ها", "ثبت شریک جدید"])
    
    with tab1:
        st.subheader("ثبت شماره تلفن جدید")
        
        partners_df = load_partners()
        partners_list = partners_df["Name"].tolist()
        partners_list.insert(0, "بدون شریک")
        
        col1, col2 = st.columns(2)
        with col1:
            phone_number = st.text_input("شماره تلفن")
            price = st.text_input("قیمت (ریال)", value="0")
        with col2:
            description = st.text_input("توضیحات (اختیاری)")
            partner_name = st.selectbox("شریک", partners_list)
        
        if st.button("ثبت شماره"):
            if not phone_number:
                st.error("لطفاً شماره تلفن را وارد کنید.")
            elif not price or parse_currency(price) <= 0:
                st.error("لطفاً قیمت معتبر وارد کنید.")
            else:
                partner_id = None
                if partner_name != "بدون شریک":
                    partner_id = partners_df[partners_df["Name"] == partner_name]["ID"].values[0]
                
                if add_phone_number(phone_number, parse_currency(price), description, partner_id):
                    st.success("شماره تلفن با موفقیت ثبت شد.")
    
    with tab2:
        st.subheader("لیست شماره‌های تلفن")
        
        df = load_phone_numbers()
        partners_df = load_partners()
        
        if df.empty:
            st.info("هیچ شماره تلفنی ثبت نشده است.")
        else:
            # تبدیل به نمایش بهتر
            display_df = df.copy()
            display_df = display_df[display_df["Status"] == "موجود"]
            
            if display_df.empty:
                st.info("هیچ شماره تلفنی موجود نیست.")
            else:
                # نمایش لیست
                for _, row in display_df.iterrows():
                    cols = st.columns([2, 2, 2, 3, 2, 2, 1, 1])
                    
                    with cols[0]:
                        st.text(row["Phone Number"])
                    with cols[1]:
                        st.text(format_currency(row["Price"]))
                    with cols[2]:
                        st.text(row["Description"] if pd.notna(row["Description"]) else "-")
                    with cols[3]:
                        partner_name = "-"
                        if pd.notna(row["Partner ID"]):
                            partner = partners_df[partners_df["ID"] == row["Partner ID"]]
                            if not partner.empty:
                                partner_name = partner["Name"].values[0]
                        st.text(partner_name)
                    with cols[4]:
                        st.text(row["Register Date"])
                    with cols[5]:
                        st.text(row["Status"])
                    with cols[6]:
                        if st.button("فروخته شد", key=f"sold_{row['ID']}"):
                            if mark_as_sold(row["ID"]):
                                st.rerun()
                    with cols[7]:
                        if st.button("حذف", key=f"del_{row['ID']}"):
                            if delete_phone_number(row["ID"]):
                                st.rerun()
    
    with tab3:
        st.subheader("ثبت شریک جدید")
        
        col1, col2 = st.columns(2)
        with col1:
            partner_name = st.text_input("نام شریک")
            partner_phone = st.text_input("شماره تماس")
        with col2:
            partner_address = st.text_area("آدرس")
        
        if st.button("ثبت شریک"):
            if not partner_name:
                st.error("لطفاً نام شریک را وارد کنید.")
            else:
                success, _ = add_partner(partner_name, partner_phone, partner_address)
                if success:
                    st.success("شریک با موفقیت ثبت شد.")
