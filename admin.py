# import streamlit as st
# import pandas as pd
# from database import create_connection
#
# st.set_page_config(page_title="Admin Panel", layout="wide")
#
# # --- Optional: Simple Password Auth ---
# PASSWORD = "admin123"
# user_pass = st.text_input("🔐 Enter Admin Password", type="password")
# if user_pass != PASSWORD:
#     st.warning("Please enter correct password to access admin features.")
#     st.stop()
#
# st.title("📋 Email Subscribers Admin Panel")
#
# # --- Delete Email Function ---
# def delete_email(email):
#     try:
#         conn = create_connection()
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         st.success(f"🗑️ Deleted {email}")
#     except Exception as e:
#         st.error(f"Error deleting {email}")
#         st.exception(e)
#
# # --- Fetch Subscribers ---
# try:
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()
#
#     df = pd.DataFrame(rows, columns=["ID", "Email", "Subscribed At"])
#
#     st.success(f"We have {len(df)} subscribers!")
#
#     # Display Table with Delete Buttons
#     for i, row in df.iterrows():
#         col1, col2, col3 = st.columns([3, 5, 2])
#         with col1:
#             st.write(f"📧 {row['Email']}")
#         with col2:
#             st.write(f"🕒 {row['Subscribed At'].strftime('%Y-%m-%d %H:%M:%S')}")
#         with col3:
#             if st.button("🗑️ Delete", key=f"delete_{row['ID']}"):
#                 delete_email(row["Email"])
#
#     # --- Export to CSV ---
#     csv = df.to_csv(index=False).encode('utf-8')
#     st.download_button("📥 Download CSV", csv, "subscribers.csv", "text/csv")
#
# except Exception as e:
#     st.error("Failed to load subscribers.")
#     st.exception(e)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from model import NewsCategorizer, FinancialNewsSentimentAnalyzer, HeadlineSelector, StockMentionMapper
from news import NewsScraper
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

SENDER_MAIL=os.getenv("SENDER_MAIL")
SENDER_PASSWORD=os.getenv("SMTP_KEY")
DB_HOST = os.getenv("DB_HOST")


def generate_html():
    date_str = datetime.now().strftime("%A, %d %B %Y")

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background-color: #f4f4f4; padding: 20px; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; }}
            h2 {{ color: #1F4E79; }}
            ul {{ padding-left: 20px; }}
            .stock {{ padding: 6px 0; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📬 Your Daily Financial Digest – {date_str}</h1>
            <h2>🔥 Top 10 Headlines</h2>
            <ul>
            <p style='text-align:center; color:#aaa;'>Built with 🧠 Streamlit & HuggingFace</p>
        </div>
    </body>
    </html>
    """
    return html

def send_all():
    recipients = ["vihansrathore2006@gmail.com"]

    html_content = generate_html()
    sent_count = 0

    for email in recipients:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "📊 Your Daily Financial Digest"
            msg["From"] = SENDER_MAIL
            msg["To"] = email
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_MAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_MAIL, email, msg.as_string())

            print(f"✅ Sent to {email}")
            sent_count += 1

        except Exception as e:
            print(f"❌ Failed for {email}: {e}")

    print(f"📤 Email sent to {sent_count} subscribers.")

send_all()