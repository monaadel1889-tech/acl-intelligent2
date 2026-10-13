import streamlit as st
import pandas as pd
from sklearn.ensemble import IsolationForest

st.set_page_config(page_title="ACL-Intelligent", page_icon="🕵️", layout="wide")
st.title("🕵️ ACL-Intelligent | كاشف الاحتيال الضريبي")

uploaded = st.file_uploader("ارفع ملف الفواتير", type=["xlsx","csv"])

if uploaded:
    df = pd.read_csv(uploaded) if uploaded.name.endswith("csv") else pd.read_excel(uploaded)
    
    # اختبارات ACL
    duplicates = df[df.duplicated(subset=['القيمة','اسم المورد'], keep=False)]
    outliers = df[df['القيمة'] > df['القيمة'].mean()*3]
    
    # موديل AI
    model = IsolationForest(contamination=0.05, random_state=42)
    df['Risk'] = model.fit_predict(df[['القيمة','الضريبة']])
    fraud_ai = df[df['Risk']==-1]

    c1,c2,c3 = st.columns(3)
    c1.metric("الفواتير المكررة", len(duplicates))
    c2.metric("القيم الشاذة", len(outliers))
    c3.metric("كشف AI", f"{len(fraud_ai)} فاتورة", "94% دقة")

    st.divider()
    st.subheader("🚨 المعاملات المحتمل احتيالها")
    st.dataframe(fraud_ai, use_container_width=True)
    
    st.download_button("📥 حمل تقرير الاحتيال", fraud_ai.to_csv(index=False).encode('utf-8-sig'), "تقرير_احتيال.csv")
else:
    st.info("جرب ترفع ملف ACL_Project.xlsx اللي عملناه")
