import json
from mail import EmailContentBuilder
from database import create_connection
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

load_dotenv()

SENDER_EMAIL = os.getenv("SMTP_MAIL")
SMTP_KEY = os.getenv("SMTP_KEY")

# Load latest preprocessed data
today = datetime.now().strftime("%Y-%m-%d")
with open(f"preprocessed_{today}.json", "r", encoding='utf-8') as f:
    data = json.load(f)

# Build Email
builder = EmailContentBuilder(
    top_headlines=data["top_headlines"],
    stock_mentions=data.get("stock_mentions", {}),
    categorized_news=data["categories"]
)
html = builder.build()

# Send to all subscribers
msg = MIMEMultipart("alternative")
msg["Subject"] = f"📰 Daily Financial Digest – {builder.today}"
msg["From"] = SENDER_EMAIL
msg.attach(MIMEText(html, "html"))

try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows, columns=["ID", "Email", "Subscribed At"])
    emails = df['Email']

    for mail in emails:
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SMTP_KEY)
                server.sendmail(SENDER_EMAIL, mail, msg.as_string())
                print(f"✅ Email sent to {mail}")
        except Exception as e:
            print(f"❌ Error sending to {mail}: {e}")
except Exception as e:
    print(f"Failed to Fetch Subscriber: {e}")
