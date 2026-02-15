import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# PDF Export
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# PAGE CONFIG (Gov Style)
# -----------------------------
st.set_page_config(
    page_title="🚦 eChallan Gov Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Theme Header
st.markdown("""
    <style>
        .main {background-color: #f8f9fa;}
        h1 {color: #003366;}
        h2 {color: #00509e;}
        .stMetric {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
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
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["day"] = df["date"].dt.day
    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("📌 Filters")

start = st.sidebar.date_input("Start Date", df["date"].min())
end = st.sidebar.date_input("End Date", df["date"].max())

filtered = df[(df["date"] >= pd.to_datetime(start)) &
              (df["date"] <= pd.to_datetime(end))]

# -----------------------------
# TITLE
# -----------------------------
st.title("🚦 eChallan Government Analytics Dashboard")
st.markdown("Interactive Dashboard with Reports, Heatmaps & Downloads")

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
# 📈 Plotly Interactive Line Chart
# =========================================================
st.subheader("📈 Interactive Challan Trend")

fig1 = px.line(
    filtered,
    x="date",
    y=["totalChallan", "disposedChallan", "pendingChallan"],
    markers=True,
    title="Daily Challan Trends"
)
st.plotly_chart(fig1, use_container_width=True)

# =========================================================
# 📊 Plotly Bar Chart
# =========================================================
st.subheader("💰 Amount Collection Comparison")

amount_df = pd.DataFrame({
    "Category": ["Pending Amount", "Disposed Amount"],
    "Amount": [
        filtered["pendingAmount"].sum(),
        filtered["disposedAmount"].sum()
    ]
})

fig2 = px.bar(
    amount_df,
    x="Category",
    y="Amount",
    text_auto=True,
    title="Pending vs Disposed Amount"
)
st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# 🥧 Donut Chart
# =========================================================
st.subheader("🥧 Pending vs Disposed Challans")

pie_df = pd.DataFrame({
    "Type": ["Disposed", "Pending"],
    "Count": [
        filtered["disposedChallan"].sum(),
        filtered["pendingChallan"].sum()
    ]
})

fig3 = px.pie(
    pie_df,
    names="Type",
    values="Count",
    hole=0.5,
    title="Challan Distribution"
)
st.plotly_chart(fig3, use_container_width=True)

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

fig4 = px.imshow(
    heatmap,
    aspect="auto",
    title="Heatmap of Challans by Day & Month"
)
st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# 📥 Download Report Buttons
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

st.success("✅ Premium Dashboard Loaded Successfully!")
