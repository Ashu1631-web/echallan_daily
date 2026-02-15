import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# PDF Export
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# PAGE CONFIG (Gov Dashboard)
# -----------------------------
st.set_page_config(
    page_title="🚦 eChallan Gov Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Custom Government UI Theme
# -----------------------------
st.markdown("""
    <style>
        .main {background-color: #f8f9fa;}
        h1 {color: #003366;}
        h2 {color: #00509e;}
        .stMetric {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    df["date"] = pd.to_datetime(df["date"])

    # Extra Features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["month_name"] = df["date"].dt.strftime("%B")
    df["day"] = df["date"].dt.day

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("📌 Dashboard Filters")

start = st.sidebar.date_input("Start Date", df["date"].min())
end = st.sidebar.date_input("End Date", df["date"].max())

filtered = df[(df["date"] >= pd.to_datetime(start)) &
              (df["date"] <= pd.to_datetime(end))]

# -----------------------------
# TITLE
# -----------------------------
st.title("🚦 eChallan Government Analytics Dashboard")
st.markdown("Interactive Dashboard with Trends, Rankings, Heatmaps & Reports")

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Challans", f"{filtered['totalChallan'].sum():,}")
col2.metric("Disposed Challans", f"{filtered['disposedChallan'].sum():,}")
col3.metric("Pending Challans", f"{filtered['pendingChallan'].sum():,}")
col4.metric("Total Amount ₹", f"{filtered['totalAmount'].sum():,}")

st.divider()

# =========================================================
# 📈 Interactive Line Trend Chart
# =========================================================
st.subheader("📈 Daily Challan Trends")

fig1 = px.line(
    filtered,
    x="date",
    y=["totalChallan", "disposedChallan", "pendingChallan"],
    markers=True,
    title="Challan Trend Over Time"
)
st.plotly_chart(fig1, use_container_width=True)

# =========================================================
# 📅 Year-wise Analysis
# =========================================================
st.subheader("📅 Year-wise Challan Summary")

yearly = filtered.groupby("year")["totalChallan"].sum().reset_index()

fig_year = px.bar(
    yearly,
    x="year",
    y="totalChallan",
    text_auto=True,
    title="Total Challans Year-wise"
)
st.plotly_chart(fig_year, use_container_width=True)

# =========================================================
# 🗓️ Month-wise Trend
# =========================================================
st.subheader("🗓️ Month-wise Challan Trend")

monthly = filtered.groupby("month_name")["totalChallan"].sum().reset_index()

fig_month = px.line(
    monthly,
    x="month_name",
    y="totalChallan",
    markers=True,
    title="Monthly Challan Trend"
)
st.plotly_chart(fig_month, use_container_width=True)

# =========================================================
# 🏆 Top 10 Highest Challan Days
# =========================================================
st.subheader("🏆 Top 10 Highest Challan Days")

top10 = filtered.sort_values("totalChallan", ascending=False).head(10)

fig_top10 = px.bar(
    top10,
    x="date",
    y="totalChallan",
    text_auto=True,
    title="Top 10 Peak Challan Dates"
)
st.plotly_chart(fig_top10, use_container_width=True)

st.dataframe(top10[["date", "totalChallan", "pendingChallan", "disposedChallan"]])

# =========================================================
# 💰 Top 10 Pending Amount Days
# =========================================================
st.subheader("💰 Top 10 Days with Highest Pending Amount")

top_amount = filtered.sort_values("pendingAmount", ascending=False).head(10)

fig_amt = px.bar(
    top_amount,
    x="date",
    y="pendingAmount",
    text_auto=True,
    title="Top 10 Pending Amount Dates"
)
st.plotly_chart(fig_amt, use_container_width=True)

# =========================================================
# 🥧 Donut Chart Distribution
# =========================================================
st.subheader("🥧 Pending vs Disposed Challans")

pie_df = pd.DataFrame({
    "Type": ["Disposed", "Pending"],
    "Count": [
        filtered["disposedChallan"].sum(),
        filtered["pendingChallan"].sum()
    ]
})

fig_pie = px.pie(
    pie_df,
    names="Type",
    values="Count",
    hole=0.5,
    title="Challan Status Distribution"
)
st.plotly_chart(fig_pie, use_container_width=True)

# =========================================================
# 🔥 Calendar Heatmap View
# =========================================================
st.subheader("🔥 Calendar Heatmap (Daily Challans Intensity)")

heatmap = filtered.pivot_table(
    values="totalChallan",
    index="day",
    columns="month",
    aggfunc="sum"
)

fig_heat = px.imshow(
    heatmap,
    aspect="auto",
    title="Heatmap of Challans by Day & Month"
)
st.plotly_chart(fig_heat, use_container_width=True)

# =========================================================
# 📥 Download Reports (Excel + PDF)
# =========================================================
st.subheader("📥 Download Reports")

# Excel Download
excel_buffer = BytesIO()
filtered.to_excel(excel_buffer, index=False, engine="openpyxl")

st.download_button(
    label="⬇️ Download Excel Report",
    data=excel_buffer.getvalue(),
    file_name="echallan_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# PDF Download
def create_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("eChallan Government Dashboard Report", styles["Title"]))
    elements.append(Paragraph(f"Total Challans: {data['totalChallan'].sum():,}", styles["Normal"]))
    elements.append(Paragraph(f"Disposed Challans: {data['disposedChallan'].sum():,}", styles["Normal"]))
    elements.append(Paragraph(f"Pending Challans: {data['pendingChallan'].sum():,}", styles["Normal"]))
    elements.append(Paragraph(f"Total Amount: ₹{data['totalAmount'].sum():,}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_file = create_pdf(filtered)

st.download_button(
    label="⬇️ Download PDF Summary",
    data=pdf_file,
    file_name="echallan_summary.pdf",
    mime="application/pdf"
)

# =========================================================
# Data Preview
# =========================================================
st.subheader("📄 Dataset Preview")
st.dataframe(filtered.tail(15))

st.success("✅ Final Premium Government Dashboard Ready!")
