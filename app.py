import streamlit as st
from database import add_subscriber, create_table
from mail import WelcomeEmailSender

st.set_page_config(page_title="📈 Financial Dashboard", layout="wide")

create_table()

# -------------------- Header --------------------
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-size: 42px; color: #1F4E79;'>📬 Stay Updated with Financial Insights</h1>
        <p style='font-size: 18px; color: #555;'>News • Sentiment • Stock Mentions — Daily</p>
    </div>
""", unsafe_allow_html=True)

# -------------------- Email Subscription --------------------
col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    with st.form("email_form", clear_on_submit=True):
        input_col, button_col = st.columns([4, 1])
        email_input = input_col.text_input("", placeholder="Enter your email", label_visibility="collapsed")
        subscribe = button_col.form_submit_button("Subscribe")
        if subscribe:
            if email_input and "@" in email_input:
                success = add_subscriber(email_input)
                if success:
                    st.success(f"{email_input} is Subscribed! Welcome to FinPulse AI ")
                    sender = WelcomeEmailSender()
                    sender.send_welcome_email(email_input)
                else:
                    st.info("You're already subscribed.")
            else:
                st.error("❌ Please enter a valid email address.")

# -------------------- Footer --------------------
st.markdown("""
    <div style='margin-top: 60px; text-align: center; color: #444; font-style: italic; font-size: 16px;'>
        “Given a 10% chance of a 100 times payoff, you should take that bet every time.”
        <br><span style='font-style: normal; font-weight: bold;'>– Jeff Bezos</span>
    </div>
    <p style='text-align:center; color:gray; margin-top: 30px;'>🧠 Built with Streamlit • Live insights powered by Transformers</p>
""", unsafe_allow_html=True)
