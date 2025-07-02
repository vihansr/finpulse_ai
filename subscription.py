import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from model import NewsCategorizer, HeadlineSelector, StockMentionMapper
from news import NewsScraper
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

SENDER_MAIL=os.getenv("SENDER_MAIL")
SENDER_PASSWORD=os.getenv("SMTP_KEY")
DB_HOST = os.getenv("DB_HOST")

class DailyNewsEmailService:
    def __init__(self, top_headlines, categorized_news, stock_mentions):
        self.top_headlines = top_headlines
        self.categorized_news = categorized_news
        self.stock_mentions = stock_mentions

    def fetch_subscribers(self):
        try:
            conn = psycopg2.connect(dsn="postgresql://marketmirror_db_user:qBYOND8sVdbH6dobJXp6fIICGtWk6OOV@dpg-d1ap9tp5pdvs73d53geg-a.oregon-postgres.render.com/marketmirror_db")
            print(f"[DEBUG] Connecting to: {DB_HOST}")
            cur = conn.cursor()
            cur.execute("SELECT email FROM subscribers")
            emails = [row[0] for row in cur.fetchall()]
            conn.close()
            return emails
        except Exception as e:
            print(f"❌ Failed to fetch subscribers: {e}")
            return []

    def generate_html(self):
        date_str = datetime.now().strftime("%A, %d %B %Y")

        stock_section = (
            ''.join(f"<div class='stock'>💹 <b>{name}</b> ({info['ticker']})</div>"
                    for name, info in self.stock_mentions[:7])
            if self.stock_mentions else "<p>No major stocks mentioned today.</p>"
        )

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
                <h2>📌 Securities to Watch Today</h2>
                {stock_section}
                <h2>🔥 Top 10 Headlines</h2>
                <ol>{''.join(f"<li>{item}</li>" for item in self.top_headlines)}</ol>

                <h2>📈 Market & Stocks</h2>
                <ul>{''.join(f"<li>{item}</li>" for item in self.categorized_news.get('Market & Stocks', [])[:5])}</ul>

                <h2>🏛️ Economy & Policy</h2>
                <ul>{''.join(f"<li>{item}</li>" for item in self.categorized_news.get('Economy & Policy', [])[:5])}</ul>

                <h2>🌍 Global & Industry</h2>
                <ul>{''.join(f"<li>{item}</li>" for item in self.categorized_news.get('Global & Industry', [])[:5])}</ul>

                <p style='text-align:center; color:#aaa;'>Team FinPulse AI</p>
            </div>
        </body>
        </html>
        """
        return html

    def send_all(self):
        recipients = self.fetch_subscribers()
        if not recipients:
            print("❌ No subscribers to send.")
            return

        html_content = self.generate_html()
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



scraper = NewsScraper()
news_list = scraper.get_all_news()

categorizer = NewsCategorizer()
categorized_news = categorizer.categorize(news_list)

selector = HeadlineSelector()
top_headlines = selector.select_top_10(news_list)

mapper = StockMentionMapper()
stock_mentions = mapper.extract_mentions(news_list)

service = DailyNewsEmailService(
    top_headlines=top_headlines,
    categorized_news=categorized_news,
    stock_mentions=stock_mentions
)
service.send_all()
