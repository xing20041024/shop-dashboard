import streamlit as st
import pandas as pd

st.set_page_config(page_title="小超市经营分析系统", layout="wide")

st.title("🛒 小超市经营分析系统（升级版）")

uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"])

if uploaded_file:

    # =====================
    # 1. 读取数据
    # =====================
    df = pd.read_excel(uploaded_file, skiprows=17)

    df.columns = df.columns.astype(str).str.strip()

    amount_col = [c for c in df.columns if "金额" in c][0]
    time_col = [c for c in df.columns if "时间" in c][0]
    type_col = [c for c in df.columns if "收/支" in c][0]

    # =====================
    # 2. 清洗
    # =====================
    df = df[df[type_col] == "收入"]
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    df = df.dropna(subset=[amount_col])

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col])

    df["日期"] = df[time_col].dt.date
    df["小时"] = df[time_col].dt.hour
    df["月份"] = df[time_col].dt.month

    # =====================
    # 3. 修复“今日收入错误”
    # =====================
    daily = df.groupby("日期")[amount_col].sum().reset_index()
    daily = daily.sort_values("日期")

    today = daily.iloc[-1][amount_col] if len(daily) > 0 else 0
    yesterday = daily.iloc[-2][amount_col] if len(daily) > 1 else 0

    mom = ((today - yesterday) / yesterday * 100) if yesterday != 0 else 0

    # =====================
    # 4. 核心指标
    # =====================
    total_income = df[amount_col].sum()

    best_day = daily.loc[daily[amount_col].idxmax()]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("总收入", f"¥{total_income:.2f}")
    col2.metric("今日收入", f"¥{today:.2f}")
    col3.metric("环比增长", f"{mom:.2f}%")
    col4.metric("最高单日", f"¥{best_day[amount_col]:.2f}")

    st.divider()

    # =====================
    # 5. 趋势图（防手机误触优化）
    # =====================
    st.subheader("📈 每日营业额")

    st.line_chart(
        daily.set_index("日期")[amount_col],
        use_container_width=True
    )

    st.divider()

    # =====================
    # 6. 时间段分析（你要的重点）
    # =====================
    st.subheader("🕒 哪个时间段最赚钱")

    hourly = df.groupby("小时")[amount_col].sum().reset_index()

    st.bar_chart(
        hourly.set_index("小时"),
        use_container_width=True
    )

    st.divider()

    # =====================
    # 7. 月份分析（中文显示）
    # =====================
    st.subheader("📅 月份收入（1=1月）")

    monthly = df.groupby("月份")[amount_col].sum().reset_index()

    st.bar_chart(
        monthly.set_index("月份"),
        use_container_width=True
    )

    st.divider()

    # =====================
    # 8. 明细（防 overflow）
    # =====================
    st.subheader("📋 最近交易")

    safe_df = df[[time_col, amount_col]].copy()
    safe_df = safe_df.sort_values(time_col, ascending=False).head(20)

    st.dataframe(safe_df.astype(str))