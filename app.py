import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="小超市经营看板", layout="wide")

# ======================
# 🟢 UI 头部优化
# ======================
st.markdown(
    """
    <h1 style='text-align:center; color:#2E86C1;'>
    🛒 小超市经营分析系统
    </h1>
    <p style='text-align:center; color:gray;'>
    经营数据实时分析看板
    </p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"])

if uploaded_file:

    # ======================
    # 1. 读取数据
    # ======================
    df = pd.read_excel(uploaded_file, skiprows=17)
    df.columns = df.columns.astype(str).str.strip()

    amount_col = [c for c in df.columns if "金额" in c][0]
    time_col = [c for c in df.columns if "时间" in c][0]
    type_col = [c for c in df.columns if "收/支" in c][0]

    # ======================
    # 2. 清洗数据
    # ======================
    df = df[df[type_col] == "收入"]
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")
    df = df.dropna(subset=[amount_col])

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col])

    df["日期"] = df[time_col].dt.date
    df["小时"] = df[time_col].dt.hour
    df["月份"] = df[time_col].dt.month   # ✅ 纯数字月份

    # ======================
    # 3. 修复“今日收入”
    # ======================
    today_date = datetime.now().date()

    today_df = df[df["日期"] == today_date]
    today_income = today_df[amount_col].sum()

    total_income = df[amount_col].sum()

    daily = df.groupby("日期")[amount_col].sum().reset_index()

    yesterday_income = (
        daily[daily["日期"] < today_date][amount_col].iloc[-1]
        if len(daily[daily["日期"] < today_date]) > 0 else 0
    )

    mom = ((today_income - yesterday_income) / yesterday_income * 100) if yesterday_income != 0 else 0

    best_day = daily.loc[daily[amount_col].idxmax()]

    # ======================
    # 4. KPI 卡片（UI升级）
    # ======================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("总收入", f"¥{total_income:.2f}")
    col2.metric("今日收入", f"¥{today_income:.2f}")
    col3.metric("环比增长", f"{mom:.2f}%")
    col4.metric("最高单日", f"¥{best_day[amount_col]:.2f}")

    st.divider()

    # ======================
    # 5. 每日营业额（修复手机缩放问题）
    # ======================
    st.subheader("📈 每日营业额趋势")

    fig1 = px.line(
        daily,
        x="日期",
        y=amount_col,
        markers=True
    )

    fig1.update_layout(
        dragmode=False
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False}
    )

    st.divider()

    # ======================
    # 6. 时间段分析（优化交互）
    # ======================
    st.subheader("🕒 哪个时间段最赚钱")

    hourly = df.groupby("小时")[amount_col].sum().reset_index()

    fig2 = px.bar(hourly, x="小时", y=amount_col)

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False}
    )

    st.divider()

    # ======================
    # 7. 月份分析（纯数字）
    # ======================
    st.subheader("📅 月份营业额（1~12月）")

    monthly = df.groupby("月份")[amount_col].sum().reset_index()

    fig3 = px.bar(monthly, x="月份", y=amount_col)

    st.plotly_chart(
        fig3,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.divider()

    # ======================
    # 8. 明细（稳定）
    # ======================
    st.subheader("📋 最近交易记录")

    st.dataframe(
        df[[time_col, amount_col]].sort_values(time_col, ascending=False).head(20).astype(str),
        use_container_width=True
    )