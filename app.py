import streamlit as st
import pandas as pd
import jdatetime
from datetime import datetime
import os

banks_file = "banks.xlsx"
transactions_file = "transactions.xlsx"
receipts_dir = "receipts"

# دیتافریم‌ها (در حافظه)
if os.path.exists(banks_file):
    df_banks = pd.read_excel(banks_file)
else:
    df_banks = pd.DataFrame(columns=["Bank Name", "Balance"])

if os.path.exists(transactions_file):
    df_transactions = pd.read_excel(transactions_file)
else:
    df_transactions = pd.DataFrame(columns=["Bank Name", "Transaction Type", "Amount", "Date", "Purpose", "Person", "Receipt"])

# ⬇ انتخاب منو
menu = st.selectbox("منو", [
    "ایجاد حساب",
    "لیست حساب‌ها",
    "تراکنش جدید"
])

# ---------------------
# 🏦 ایجاد حساب جدید
# ---------------------
if menu == "ایجاد حساب":
    st.header("ایجاد حساب بانکی جدید")
    bank_name = st.text_input("نام بانک")
    amount = st.text_input("مبلغ اولیه")

    if st.button("ایجاد حساب"):
        try:
            initial_amount = float(amount.replace(",", "").replace("-", "").replace(" ", ""))
            if bank_name in df_banks["Bank Name"].values:
                st.warning("این بانک قبلاً وجود دارد.")
            else:
                df_banks.loc[len(df_banks)] = [bank_name, initial_amount]
                df_banks.to_excel(banks_file, index=False)
                st.success(f"بانک {bank_name} با مبلغ {initial_amount:,.0f} ایجاد شد.")
        except ValueError:
            st.error("مبلغ معتبر نیست. لطفاً عدد وارد کنید.")

# ---------------------
# 📄 لیست حساب‌ها
# ---------------------
elif menu == "لیست حساب‌ها":
    st.header("لیست حساب‌های موجود")
    if df_banks.empty:
        st.info("هیچ حسابی موجود نیست.")
    else:
        st.table(df_banks)

# ---------------------
# 💸 تراکنش
# ---------------------
elif menu == "تراکنش جدید":
    st.header("ثبت تراکنش")

    if df_banks.empty:
        st.warning("هیچ بانکی وجود ندارد. ابتدا یک حساب ایجاد کنید.")
    else:
        selected_bank = st.selectbox("انتخاب بانک", df_banks["Bank Name"].tolist())
        transaction_type = st.radio("نوع تراکنش", ["واریز", "برداشت"])
        amount = st.text_input("مبلغ")
        purpose = st.text_input("علت تراکنش")
        person = st.text_input("شخص / شرکت")
        date_choice = st.radio("تاریخ", ["تاریخ امروز", "ورود دستی"])
        if date_choice == "ورود دستی":
            date = st.text_input("تاریخ (YYYY/MM/DD)")
        else:
            date = jdatetime.datetime.today().strftime("%Y/%m/%d")

        receipt = st.file_uploader("آپلود تصویر رسید (اختیاری)", type=["jpg", "png", "jpeg"])

        if st.button("ثبت تراکنش"):
            try:
                transaction_amount = float(amount.replace(",", "").replace("-", "").replace(" ", ""))
                current_balance = df_banks.loc[df_banks['Bank Name'] == selected_bank, 'Balance'].values[0]
                new_balance = current_balance + transaction_amount if transaction_type == "واریز" else current_balance - transaction_amount

                df_banks.loc[df_banks["Bank Name"] == selected_bank, "Balance"] = new_balance
                df_banks.to_excel(banks_file, index=False)

                # ذخیره تصویر رسید
                receipt_path = ""
                if receipt is not None:
                    os.makedirs(receipts_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    receipt_path = os.path.join(receipts_dir, f"{person}_{timestamp}.jpg")
                    with open(receipt_path, "wb") as f:
                        f.write(receipt.getbuffer())

                new_transaction = pd.DataFrame([[selected_bank, transaction_type, transaction_amount, date, purpose, person, receipt_path]],
                                               columns=["Bank Name", "Transaction Type", "Amount", "Date", "Purpose", "Person", "Receipt"])
                df_transactions = pd.concat([df_transactions, new_transaction], ignore_index=True)
                df_transactions.to_excel(transactions_file, index=False)

                st.success("تراکنش با موفقیت ثبت شد.")
            except ValueError:
                st.error("مقدار وارد شده برای مبلغ معتبر نیست.")
