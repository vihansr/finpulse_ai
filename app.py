import streamlit as st
import json
from graphs import SentimentPieChart
from database import create_table, add_subscriber
from mail import WelcomeEmailSender
from datetime import datetime
import glob

create_table()

st.set_page_config(
    page_title="Financial News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_latest_data():
    files = glob.glob("preprocessed_*.json")
    if not files:
        return None
    latest_file = max(files, key=lambda f: f)
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_latest_data()

if not data:
    st.error("No data available. Please run the preprocessor.")
    st.stop()


overall_news = data["news"]
sentiment_results = data["sentiment"]
top_headlines = data["top_headlines"]
categorized_news = data["categories"]
stock_mentions = data.get("stock_mentions", [])

# Header Section
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-size: 42px; color: #1F4E79;'>📊 Financial News & Sentiment Dashboard</h1>
        <p style='font-size: 18px; color: #555;'>Stay ahead with real-time news analysis and market sentiment insights</p>
    </div>
""", unsafe_allow_html=True)

# Single Column Layout
with st.container():
    pos_count = sum(1 for s in sentiment_results if s["label"].lower() == "positive")
    neg_count = sum(1 for s in sentiment_results if s["label"].lower() == "negative")

    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("🟢 Positive Sentiments", value=pos_count)
    with metric_col2:
        st.metric("🔴 Negative Sentiments", value=neg_count)

    st.markdown("</div>", unsafe_allow_html=True)

    pie = SentimentPieChart(sentiment_results)
    pie.generate()

# Top 10 Headlines
st.divider()
st.subheader("🔥 Top 10 Headlines")

for idx, headline in enumerate(top_headlines[:10], start=1):
    st.markdown(f"""
    <div style='
        padding: 12px;
        background-color: #e8f0fe;
        color: #1a1a1a;
        border-left: 5px solid #1a73e8;
        margin-bottom: 10px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        font-size: 16px;
        font-weight: 500;
    '>
        <span style="color: #1a73e8;">{idx}.</span> {headline}
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

import streamlit as st

st.subheader("📌 Stocks to Watch Today")


if stock_mentions:
    for name, info in stock_mentions:
        st.markdown(f"""
        <div style='padding: 8px 0;'>
            🔹 <strong>{name}</strong> <span style='color:gray;'>({info['ticker']})</span>
            — mentioned <span style='color:#1f77b4;'>{info['count']} time{'s' if info['count'] > 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No significant stock mentions found.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

#Categorized News
st.subheader("🗂️ Explore Categorized News")

# Initialize session state
if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = "Market & Stocks"

categories = {
    "📈 Market & Stocks": "Market & Stocks",
    "🏛️ Economy & Policy": "Economy & Policy",
    "🌍 Global & Industry": "Global & Industry"
}

col1, col2, col3 = st.columns([1, 1, 1], gap="small")
for i, (label, key) in enumerate(categories.items()):
    with [col1, col2, col3][i]:
        if st.button(label, use_container_width=True):
            st.session_state["selected_category"] = key

selected_category = st.session_state["selected_category"]



selected_news = categorized_news.get(selected_category, [])[:10]

if selected_news:
    for idx, item in enumerate(selected_news, start=1):
        st.markdown(f"""
        <div style='
            background-color: #ffffff;
            color: #111827;
            padding: 12px;
            border-left: 4px solid #6366f1;
            margin-bottom: 10px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            font-size: 15px;
        '>
            <b style="color:#6366f1;">{idx}.</b> {item}
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No news found in this category.")

# Footer Divider
st.markdown("---")

# 📬 Email Subscription Section at Bottom
st.markdown(
    "<h3 style='text-align: center;'>📬 Stay Updated with Daily Financial Insights</h3>",
    unsafe_allow_html=True
)
# Centering the form layout
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    with st.form("email_form", clear_on_submit=True):
        # Create two columns for email input and subscribe button
        input_col, button_col = st.columns([4, 1])

        email_input = input_col.text_input(
            label="",
            placeholder="Enter your email...",
            label_visibility="collapsed"
        )

        subscribe = button_col.form_submit_button("Subscribe")

        if subscribe:
            if email_input and "@" in email_input:
                success = add_subscriber(email_input)
                if success:
                    st.success(f"You are Subscribed! We have sent an email to {email_input}.")

                    sender = WelcomeEmailSender()
                    sender.send_welcome_email(email_input)
                else:
                    st.info("You're already subscribed.")
            else:
                st.error("Please enter a valid email address.")

# Full News Archive
st.divider()
with st.expander("📚 View Full News Archive"):
    for idx, item in enumerate(overall_news, start=1):
        st.markdown(f"{idx}. {item}")

st.markdown("🧠 Built with `Streamlit`, `Transformers`, and 🤖 HuggingFace • 📬 Subscribe to daily insights.")
