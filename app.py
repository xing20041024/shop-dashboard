import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="兴旺超市经营分析系统",
    page_icon="🛒",
    layout="wide"
)

# ==========================
# 页面标题
# ==========================
st.markdown(
    """
    <div style='text-align:center;padding:10px'>
        <h1>🛒 兴旺超市经营分析系统</h1>
        <p style='color:gray'>
        实时查看营业情况 · 数据驱动经营
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "上传微信账单Excel",
    type=["xlsx"]
)

if uploaded_file:

    try:

        # ==========================
        # 读取微信账单
        # ==========================
        df = pd.read_excel(
            uploaded_file,
            skiprows=17
        )

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        amount_col = [
            c for c in df.columns
            if "金额" in c
        ][0]

        time_col = [
            c for c in df.columns
            if "时间" in c
        ][0]

        type_col = [
            c for c in df.columns
            if "收/支" in c
        ][0]

        # ==========================
        # 数据清洗
        # ==========================
        df = df[df[type_col] == "收入"]

        df[amount_col] = pd.to_numeric(
            df[amount_col],
            errors="coerce"
        )

        df = df.dropna(
            subset=[amount_col]
        )

        df[time_col] = pd.to_datetime(
            df[time_col],
            errors="coerce"
        )

        df = df.dropna(
            subset=[time_col]
        )

        df["日期"] = df[time_col].dt.date
        df["小时"] = df[time_col].dt.hour
        df["月份"] = df[time_col].dt.month
        df["星期"] = df[time_col].dt.dayofweek

        weekday_map = {
            0:"周一",
            1:"周二",
            2:"周三",
            3:"周四",
            4:"周五",
            5:"周六",
            6:"周日"
        }

        df["星期名称"] = (
            df["星期"]
            .map(weekday_map)
        )

        # ==========================
        # 今日收入（真实日期）
        # ==========================
        today = datetime.now().date()

        today_income = df[
            df["日期"] == today
        ][amount_col].sum()

        total_income = df[
            amount_col
        ].sum()

        # ==========================
        # 每日汇总
        # ==========================
        daily = (
            df.groupby("日期")[amount_col]
            .sum()
            .reset_index()
            .sort_values("日期")
        )

        # 昨日收入
        before_today = daily[
            daily["日期"] < today
        ]

        if len(before_today) > 0:
            yesterday_income = (
                before_today
                .iloc[-1][amount_col]
            )
        else:
            yesterday_income = 0

        if yesterday_income != 0:
            growth = (
                (today_income - yesterday_income)
                / yesterday_income
                * 100
            )
        else:
            growth = 0

        # ==========================
        # 本月收入
        # ==========================
        current_month = today.month

        month_income = df[
            df["月份"] == current_month
        ][amount_col].sum()

        # ==========================
        # 最高营业日
        # ==========================
        best_day = daily.loc[
            daily[amount_col].idxmax()
        ]

        best_day_date = best_day["日期"]
        best_day_income = best_day[amount_col]

        # ==========================
        # 高峰时段
        # ==========================
        hourly = (
            df.groupby("小时")[amount_col]
            .sum()
            .reset_index()
        )

        peak_hour = hourly.loc[
            hourly[amount_col].idxmax()
        ]["小时"]

        # ==========================
        # 平均每笔消费
        # ==========================
        avg_order = (
            total_income / len(df)
            if len(df) > 0
            else 0
        )

        # ==========================
        # 最近7天平均营业额
        # ==========================
        last7 = daily.tail(7)

        avg7 = (
            last7[amount_col].mean()
            if len(last7) > 0
            else 0
        )

        # ==========================
        # 最赚钱星期
        # ==========================
        week_income = (
            df.groupby("星期名称")[amount_col]
            .sum()
        )

        best_weekday = (
            week_income.idxmax()
        )

        # ==========================
        # KPI展示
        # ==========================
        col1,col2,col3,col4 = st.columns(4)

        col1.metric(
            "今日收入",
            f"¥{today_income:.2f}"
        )

        col2.metric(
            "本月收入",
            f"¥{month_income:.2f}"
        )

        col3.metric(
            "总收入",
            f"¥{total_income:.2f}"
        )

        col4.metric(
            "环比",
            f"{growth:.1f}%"
        )

        st.divider()

        col5,col6,col7,col8 = st.columns(4)

        col5.metric(
            "最高营业日",
            f"{best_day_date}"
        )

        col6.metric(
            "最高营业额",
            f"¥{best_day_income:.2f}"
        )

        col7.metric(
            "高峰时段",
            f"{int(peak_hour)}点"
        )

        col8.metric(
            "平均每单",
            f"¥{avg_order:.2f}"
        )

        st.info(
            f"📊 最近7天平均营业额：¥{avg7:.2f} ｜ "
            f"🔥 最赚钱星期：{best_weekday}"
        )

        # ==========================
        # 每日营业额趋势
        # ==========================
        st.subheader("📈 每日营业额趋势")

        fig1 = px.line(
            daily,
            x="日期",
            y=amount_col,
            markers=True
        )

        fig1.update_xaxes(
            tickformat="%m/%d"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": True
            }
        )

        # ==========================
        # 小时收入
        # ==========================
        st.subheader("🕒 小时收入分布")

        fig2 = px.bar(
            hourly,
            x="小时",
            y=amount_col
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": True
            }
        )

        # ==========================
        # 星期收入
        # ==========================
        st.subheader("📅 星期收入分布")

        week_df = (
            df.groupby("星期名称")[amount_col]
            .sum()
            .reindex(
                ["周一","周二","周三","周四","周五","周六","周日"]
            )
            .reset_index()
        )

        fig3 = px.bar(
            week_df,
            x="星期名称",
            y=amount_col
        )

        st.plotly_chart(
            fig3,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "staticPlot": True
            }
        )

        # ==========================
        # 最近交易
        # ==========================
        st.subheader("📋 最近交易")

        show_df = df[
            [time_col, amount_col]
        ].copy()

        show_df = show_df.sort_values(
            time_col,
            ascending=False
        ).head(20)

        st.dataframe(
            show_df.astype(str),
            use_container_width=True
        )

    except Exception as e:
        st.error(f"读取失败：{e}")