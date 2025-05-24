# engine.py
import pandas as pd
import jdatetime
from datetime import datetime

def get_today_jalali_str():
    """تاریخ امروز به فرمت شمسی (yyyy/mm/dd)"""
    return jdatetime.date.today().strftime("%Y/%m/%d")

def filter_today_transactions(df):
    """فیلتر کردن تراکنش‌هایی که مربوط به تاریخ امروز هستند"""
    today_jalali = get_today_jalali_str()
    return df[df["Date"] == today_jalali].copy()


def update_bank_balance(df_banks, bank_name, amount, operation):
    """
    به‌روزرسانی موجودی بانک.
    :param df_banks: دیتافریم بانک‌ها
    :param bank_name: نام بانک
    :param amount: مبلغ
    :param operation: "add" یا "subtract"
    :return: df_banks به‌روزشده یا None اگر خطا بود
    """
    if bank_name not in df_banks["Bank Name"].values:
        return None

    current_balance = df_banks.loc[df_banks["Bank Name"] == bank_name, "Balance"].values[0]

    if operation == "add":
        new_balance = current_balance + amount
    elif operation == "subtract":
        new_balance = current_balance - amount
    else:
        return None

    if new_balance < 0:
        return None

    df_banks.loc[df_banks["Bank Name"] == bank_name, "Balance"] = new_balance
    return df_banks

def delete_transaction(df_banks, df_transactions, index):
    """
    حذف یک تراکنش و بروزرسانی موجودی بانک
    :param df_banks: دیتافریم بانک‌ها
    :param df_transactions: دیتافریم تراکنش‌ها
    :param index: ایندکس تراکنش مورد نظر برای حذف
    :return: df_banks, df_transactions یا None در صورت خطا
    """
    try:
        row = df_transactions.loc[index]
        bank = row["Bank Name"]
        amount = float(row["Amount"])
        trans_type = row["Transaction Type"]

        # اگر تراکنش از نوع واریز است، باید مبلغ از موجودی کم شود و بالعکس
        if trans_type == "واریز":
            df_banks = update_bank_balance(df_banks, bank, amount, "subtract")
        elif trans_type == "برداشت":
            df_banks = update_bank_balance(df_banks, bank, amount, "add")
        else:
            return None, None

        # حذف تراکنش
        df_transactions = df_transactions.drop(index).reset_index(drop=True)

        return df_banks, df_transactions
    except Exception as e:
        print("Error in delete_transaction:", e)
        return None, None
    
    
    
