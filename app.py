import streamlit as st
import pandas as pd

st.title("小超市营业额看板")

uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.success("上传成功")

    st.write(df.head())

    st.metric("总收入", df["金额"].sum())