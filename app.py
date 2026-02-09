import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="EduPro Dashboard", layout="wide")

st.title("📊 EDUPRO LEARNER INTELLIGENCE DASHBOARD")

# Load Data
@st.cache_data
def load_data():
    users = pd.read_csv("users.csv")
    teachers = pd.read_csv("teachers.csv")
    courses = pd.read_csv("courses.csv")
    transactions = pd.read_csv("transactions.csv")

    master = transactions.merge(users, on="UserID", how="left") \
                         .merge(courses, on="CourseID", how="left") \
                         .merge(teachers, on="TeacherID", how="left")

    return master

master = load_data()

# Clean Column Names
master = master.rename(columns={
    "Age_x": "UserAge",
    "Gender_x": "UserGender",
    "Age_y": "TeacherAge",
    "Gender_y": "TeacherGender"
})

# Create Age Band
bins = [0, 18, 25, 35, 45, 100]
labels = ["<18", "18-25", "26-35", "36-45", "45+"]
master["AgeBand"] = pd.cut(master["UserAge"], bins=bins, labels=labels)

# Sidebar Filters
st.sidebar.header("🔎 FILTERS")

selected_age = st.sidebar.multiselect(
    "Select Age Band",
    options=master["AgeBand"].dropna().unique(),
    default=master["AgeBand"].dropna().unique()
)

selected_gender = st.sidebar.multiselect(
    "Select Gender",
    options=master["UserGender"].unique(),
    default=master["UserGender"].unique()
)

filtered_data = master[
    (master["AgeBand"].isin(selected_age)) &
    (master["UserGender"].isin(selected_gender))
]

# KPI Section
st.subheader("📌 PLATFORM OVERVIEW")

total_users = filtered_data["UserID"].nunique()
total_enrollments = filtered_data["TransactionID"].count()
total_revenue = filtered_data["Amount"].sum()

avg_courses = 0
if total_users > 0:
    avg_courses = total_enrollments / total_users

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", total_users)
col2.metric("Total Enrollments", total_enrollments)
col3.metric("Total Revenue", f"${total_revenue:,.2f}")
col4.metric("Avg Courses per User", round(avg_courses, 2))

# Tabs Section
tab1, tab2, tab3 = st.tabs(["DEMOGRAPHICS", " COURSE DEMAND", "REVENUE"])

# Demographics Tab
with tab1:
    st.subheader("Age Distribution")
    age_dist = filtered_data[["UserID", "AgeBand"]].drop_duplicates()["AgeBand"].value_counts()
    st.bar_chart(age_dist)

    st.subheader("Gender Distribution")
    gender_dist = filtered_data[["UserID", "UserGender"]].drop_duplicates()["UserGender"].value_counts()
    st.bar_chart(gender_dist)

# Course Demand Tab
with tab2:
    st.subheader("Course Category Distribution")
    category_dist = filtered_data["CourseCategory"].value_counts().sort_values(ascending=False)
    st.bar_chart(category_dist)

    st.subheader("Course Level Distribution")
    level_dist = filtered_data["CourseLevel"].value_counts()
    st.bar_chart(level_dist)

# Revenue Tab
with tab3:
    st.subheader("Revenue by Category")
    revenue_by_category = filtered_data.groupby("CourseCategory")["Amount"].sum().sort_values(ascending=False)
    st.bar_chart(revenue_by_category)

    st.subheader("Revenue by Age Group")
    revenue_by_age = filtered_data.groupby("AgeBand")["Amount"].sum()
    st.bar_chart(revenue_by_age)
