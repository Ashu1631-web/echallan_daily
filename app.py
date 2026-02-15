import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="eChallan Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("📌 Filter Options")

start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) &
                 (df["date"] <= pd.to_datetime(end_date))]

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("🚦 eChallan Daily Dashboard")
st.markdown("Professional Analytics Dashboard with KPIs, Graphs & Charts")

# -----------------------------
# KPI Section
# -----------------------------
total_challan = filtered_df["totalChallan"].sum()
disposed_challan = filtered_df["disposedChallan"].sum()
pending_challan = filtered_df["pendingChallan"].sum()
total_amount = filtered_df["totalAmount"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Challans", f"{total_challan:,}")
col2.metric("Disposed Challans", f"{disposed_challan:,}")
col3.metric("Pending Challans", f"{pending_challan:,}")
col4.metric("Total Amount (₹)", f"{total_amount:,}")

st.divider()

# -----------------------------
# Line Chart Trend
# -----------------------------
st.subheader("📈 Challan Trend Over Time")

fig, ax = plt.subplots()
ax.plot(filtered_df["date"], filtered_df["totalChallan"], label="Total Challans")
ax.plot(filtered_df["date"], filtered_df["disposedChallan"], label="Disposed")
ax.plot(filtered_df["date"], filtered_df["pendingChallan"], label="Pending")

ax.set_xlabel("Date")
ax.set_ylabel("Count")
ax.legend()

st.pyplot(fig)

st.divider()

# -----------------------------
# Bar Chart (Amounts)
# -----------------------------
st.subheader("💰 Amount Collection Comparison")

amount_data = pd.DataFrame({
    "Type": ["Pending Amount", "Disposed Amount"],
    "Amount": [
        filtered_df["pendingAmount"].sum(),
        filtered_df["disposedAmount"].sum()
    ]
})

fig2, ax2 = plt.subplots()
ax2.bar(amount_data["Type"], amount_data["Amount"])
ax2.set_ylabel("Amount (₹)")

st.pyplot(fig2)

st.divider()

# -----------------------------
# Pie Chart (Disposed vs Pending)
# -----------------------------
st.subheader("🥧 Pending vs Disposed Challans")

pie_values = [
    disposed_challan,
    pending_challan
]

pie_labels = ["Disposed", "Pending"]

fig3, ax3 = plt.subplots()
ax3.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90)
ax3.axis("equal")

st.pyplot(fig3)

st.divider()

# -----------------------------
# Data Table
# -----------------------------
st.subheader("📄 Dataset Preview")
st.dataframe(filtered_df.head(20))

st.success("✅ Dashboard Loaded Successfully!")
