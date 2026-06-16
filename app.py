import streamlit as st
import pandas as pd

st.set_page_config(page_title="小超市经营分析系统", layout="wide")

st.title("🛒 小超市经营分析系统")

uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"])

if uploaded_file:

    # =========================
    # 1. 读取数据（稳定版）
    # =========================
    df = pd.read_excel(uploaded_file, skiprows=17)

    st.success("文件上传成功")

    # 清理列名（防止空格/异常）
    df.columns = df.columns.astype(str).str.strip()

    st.write("📌 数据列名：", df.columns)

    # =========================
    # 2. 自动识别关键列
    # =========================
    amount_col = [c for c in df.columns if "金额" in c][0]
    time_col = [c for c in df.columns if "时间" in c][0]
    type_col = [c for c in df.columns if "收/支" in c][0]

    # =========================
    # 3. 数据清洗
    # =========================
    df = df[df[type_col] == "收入"]

    df[time_col] = pd.to_datetime(df[time_col])
    df["日期"] = df[time_col].dt.date
    df["小时"] = df[time_col].dt.hour

    # =========================
    # 4. 核心指标
    # =========================
    total_income = df[amount_col].sum()

    daily = df.groupby("日期")[amount_col].sum().reset_index()

    today = daily[amount_col].iloc[-1] if len(daily) > 0 else 0
    yesterday = daily[amount_col].iloc[-2] if len(daily) > 1 else 0

    mom = ((today - yesterday) / yesterday * 100) if yesterday != 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("总收入", f"¥{total_income:.2f}")
    col2.metric("今日收入", f"¥{today:.2f}")
    col3.metric("环比增长", f"{mom:.2f}%")

    st.divider()

    # =========================
    # 5. 趋势图
    # =========================
    st.subheader("📈 每日营业额趋势")
    st.line_chart(daily.set_index("日期")[amount_col])

    st.divider()

    # =========================
    # 6. 小时分析
    # =========================
    st.subheader("🕒 每小时收入分布")

    hourly = df.groupby("小时")[amount_col].sum()
    st.bar_chart(hourly)

    st.divider()

    # =========================
    # 7. 明细
    # =========================
    st.subheader("📋 最近交易")

    st.dataframe(
        df.sort_values(time_col, ascending=False).head(20)
    )