import streamlit as st
import pandas as pd

st.set_page_config(page_title="ACL-Intelligent", page_icon="🧾")
st.title("ACL-Intelligent | كاشف الاحتيال الضريبي")
st.write("ارفع ملف الفواتير وسيتم كشف الفواتير المشبوهة تلقائيا")

file = st.file_uploader("اختر ملف Excel", type=["xlsx","csv","xls"])

if file:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.success(f"تم تحميل {len(df)} فاتورة")
    st.dataframe(df.head(20), use_container_width=True)

    # تحليل ذكي يشتغل مع أي أسماء أعمدة
    # هنحاول نلاقي عمود المبلغ والضريبة تلقائيا
    amount_col = None
    vat_col = None
    for col in df.columns:
        c = str(col).lower()
        if "amount" in c or "مبلغ" in c or "قيمة" in c:
            if "vat" not in c and "ضريبة" not in c:
                amount_col = col
        if "vat" in c or "ضريبة" in c or "tax" in c:
            vat_col = col

    # لو ملقيناش، ناخد أول عمودين أرقام
    if amount_col is None:
        num_cols = df.select_dtypes(include='number').columns.tolist()
        if len(num_cols) >= 2:
            amount_col = num_cols[0]
            vat_col = num_cols[1]

    st.write(f"عمود المبلغ: {amount_col} | عمود الضريبة: {vat_col}")

    def is_fraud(row):
        try:
            if amount_col and vat_col:
                amt = float(row[amount_col])
                vat = float(row[vat_col])
                # الضريبة المفروض 14%
                if amt > 0:
                    rate = vat / amt
                    if rate < 0.05 or rate > 0.25: # مش 14%
                        return "🚨 ضريبة غير صحيحة"
                    if amt > 300000:
                        return "🚨 مبلغ ضخم"
            return "✅ سليم"
        except:
            return "✅ سليم"

    df["الحالة"] = df.apply(is_fraud, axis=1)
    frauds = df[df["الحالة"].str.contains("🚨")]

    st.subheader(f"عدد الفواتير المشبوهة: {len(frauds)} من {len(df)}")
    if len(frauds) > 0:
        st.dataframe(frauds, use_container_width=True)
        st.bar_chart(frauds[amount_col] if amount_col else frauds.iloc[:,0])
    else:
        st.info("لم يتم العثور على احتيال")
else:
    st.info("في انتظار رفع الملف...")
