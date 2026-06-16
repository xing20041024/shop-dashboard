import streamlit as   作为 st
import pandas as pd   以pd方式导入熊猫

st.set_page_config(page_title="小超市经营分析系统", layout="wide")st.set_page_config(page_title="小超市经营分析系统", layout="wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide"   "wide")

st.title("🛒 小超市经营分析系统（完整版）")

uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"])uploaded_file = st.file_uploader("上传微信账单Excel", type=["xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"   "xlsx"])

if uploaded_file:   如果uploaded_file:

    # =====================
    # 1. 读取数据
    # =====================
    df = pd.read_excel(uploaded_file, skiprows=17)Df = pd。read_excel (uploaded_file skiprows = 17)

    st.success("文件读取成功")

    # =====================
    # 2. 数据清洗
    # =====================
    df = df[df["收/支"] == "收入"]
    df["交易时间"] = pd.to_datetime(df["交易时间"])
    df["日期"] = df["交易时间"].dt.date
    df["小时"] = df["交易时间"].dt.hour

    amount_col = "金额(元)"

    # =====================
    # 3. 核心指标
    # =====================
    total_income = df[amount_col].sum()

    daily = df.groupby("日期")[amount_col].sum().reset_index()

    today = daily["金额(元)"].iloc[-1]
    yesterday = daily["金额(元)"].iloc[-2] if len(daily) > 1 else 0

    mom = ((today - yesterday) / yesterday * 100) if yesterday != 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("总收入", f"¥{total_income:.2f}")
    col2.metric("今日收入", f"¥{today:.2f}")
    col3.metric("环比增长", f"{mom:.2f}%")

    st.divider()

    # =====================
    # 4. 趋势图
    # =====================
    st.subheader("📈 营业额趋势")

    st.line_chart(daily.set_index("日期")[amount_col])

    st.divider()

    # =====================
    # 5. 时间段分析
    # =====================
    st.subheader("🕒 每小时收入分布")

    hourly = df.groupby("小时")[amount_col].sum()

    st.bar_chart(hourly)

    st.divider()

    # =====================
    # 6. 明细数据
    # =====================
    st.subheader("📋 最近交易记录")st.subheader   小标题("📋 最近交易记录")

    st.dataframe(df.sort_values("交易时间", ascending=False).head(20))st.dataframe(df.sort_values("交易时间", ascending=False   假).head   头(20))
