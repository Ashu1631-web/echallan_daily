import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config("🚦 eChallan Analytics Dashboard", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("📌 Dashboard Filters")

start = st.sidebar.date_input("Start Date", df["date"].min())
end = st.sidebar.date_input("End Date", df["date"].max())

filtered = df[(df["date"] >= pd.to_datetime(start)) &
              (df["date"] <= pd.to_datetime(end))]

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("🚦 eChallan Professional Analytics Dashboard")
st.markdown("Multiple Chart Types | KPIs | Trends | Distribution")

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Challans", f"{filtered['totalChallan'].sum():,}")
col2.metric("Disposed Challans", f"{filtered['disposedChallan'].sum():,}")
col3.metric("Pending Challans", f"{filtered['pendingChallan'].sum():,}")
col4.metric("Total Amount ₹", f"{filtered['totalAmount'].sum():,}")

st.divider()

# =========================================================
# 📌 CHART 1: LINE TREND
# =========================================================
st.subheader("📈 Line Chart - Challan Trend Over Time")

fig, ax = plt.subplots()
ax.plot(filtered["date"], filtered["totalChallan"], label="Total")
ax.plot(filtered["date"], filtered["disposedChallan"], label="Disposed")
ax.plot(filtered["date"], filtered["pendingChallan"], label="Pending")
ax.legend()
st.pyplot(fig)

# =========================================================
# 📌 CHART 2: AREA CHART
# =========================================================
st.subheader("🌊 Area Chart - Pending Challans Growth")

st.area_chart(filtered.set_index("date")["pendingChallan"])

# =========================================================
# 📌 CHART 3: BAR CHART (Horizontal)
# =========================================================
st.subheader("📊 Horizontal Bar - Amount Comparison")

amounts = {
    "Pending Amount": filtered["pendingAmount"].sum(),
    "Disposed Amount": filtered["disposedAmount"].sum()
}

fig2, ax2 = plt.subplots()
ax2.barh(list(amounts.keys()), list(amounts.values()))
st.pyplot(fig2)

# =========================================================
# 📌 CHART 4: DONUT PIE CHART
# =====================================
