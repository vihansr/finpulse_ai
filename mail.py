import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# class NewsEmailSender:
#     def __init__(self, recipient_list, news_list, subject="📰 Daily Stock Market News Digest"):
#         load_dotenv()
#         self.smtp_key = os.getenv("SMTP_KEY")
#         self.sender_email = os.getenv("SENDER_MAIL")
#         self.recipient_list = recipient_list
#         self.news_list = news_list
#         self.subject = subject
#
#     def format_html_content(self):
#         formatted_news = "<br><br>".join([f"• {headline}" for headline in self.news_list])
#         html = f"""
#         <html>
#           <body>
#             <h3>Here's your daily dose of Business Standard news:</h3>
#             <ol>{formatted_news}</ol>
#             <br>
#             <p style="font-size:12px; color:gray;">Sent via Python script</p>
#           </body>
#         </html>
#         """
#         return html
#
#     def send_emails(self):
#         html_content = self.format_html_content()
#
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = self.subject
#         msg["From"] = self.sender_email
#         msg.attach(MIMEText(html_content, "html"))
#
#         for recipient in self.recipient_list:
#             msg["To"] = recipient
#             try:
#                 with smtplib.SMTP("smtp.gmail.com", 587) as server:
#                     server.starttls()
#                     server.login(self.sender_email, self.smtp_key)
#                     server.sendmail(self.sender_email, recipient, msg.as_string())
#                     print(f"✅ Email sent to {recipient}")
#             except Exception as e:
#                 print(f"❌ Failed to send email to {recipient}: {e}")


class WelcomeEmailSender:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_MAIL")
        self.smtp_key = os.getenv("SMTP_KEY")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_welcome_email(self, recipient_email):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to FinPulse AI – Your Smart Financial News Companion!"
        msg["From"] = self.sender_email
        msg["To"] = recipient_email

        html = f"""\
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <h2>👋 Welcome to <span style="color:#0e76a8;">FinPulse AI</span>!</h2>

    <p>Thanks for subscribing! 🎉 You're now part of a community that stays ahead of the curve with:</p>

    <ul>
      <li>📈 Daily Financial News Highlights</li>
      <li>🧠 AI-Powered Sentiment Analysis</li>
      <li>📰 Curated Summaries You Can Trust</li>
    </ul>

    <p>We’ll deliver fresh market updates straight to your inbox every day.</p>

    <p>Got feedback or suggestions? Just hit reply — we’d love to hear from you!</p>

    <p>Cheers, <br> Team FinPulse AI</p>

    <hr style="margin-top: 30px;" />
    <p style="font-size: 12px; color: #888;">You’re receiving this email because you subscribed on our site. You can unsubscribe anytime.</p>
  </body>
</html>
"""

        content = MIMEText(html, "html")

        msg.attach(content)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.smtp_key)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
                print(f"✅ Welcome email sent to {recipient_email}")
        except Exception as e:
            print(f"❌ Failed to send welcome email to {recipient_email}: {e}")



from datetime import datetime

class EmailContentBuilder:
    def __init__(self, top_headlines, stock_mentions, categorized_news):
        self.top_headlines = top_headlines[:5]
        self.stock_mentions = stock_mentions
        self.categorized_news = categorized_news
        self.today = datetime.now().strftime("%B %d, %Y")

    def _render_list(self, items):
        return "\n".join([f"<li>{item}</li>" for item in items])

    def _render_stocks(self):
        items = [
            f"<li><strong>{company}</strong> ({ticker})</li>"
            for company, ticker in list(self.stock_mentions.items())[:3]
        ]
        return "\n".join(items)

    def _get_category_section(self, title, color, items):
        return f"""
        <h4 style="color: {color};">{title}</h4>
        <ul style="padding-left: 20px;">{self._render_list(items[:3])}</ul>
        """

    def build(self):
        html = f"""
        <html>
          <body style="font-family: 'Segoe UI', sans-serif; background-color: #F9FAFB; padding: 30px; color: #1E293B;">
            <div style="max-width: 700px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 6px 20px rgba(0,0,0,0.04);">

              <h2 style="color: #0F172A; margin-bottom: 5px;">📊 Your Daily Financial Brief</h2>
              <p style="font-size: 14px; color: #64748B; margin-bottom: 25px;">
                Here's your curated stock market update for <strong>{self.today}</strong>.
              </p>

              <h3 style="color: #1D4ED8;">📰 Top 5 Headlines</h3>
              <ol style="padding-left: 20px; color: #1E293B;">
                {self._render_list(self.top_headlines)}
              </ol>

              <h3 style="color: #DC2626; margin-top: 30px;">📈 3 Stocks to Watch</h3>
              <ul style="padding-left: 20px;">
                {self._render_stocks()}
              </ul>

              <h3 style="color: #16A34A; margin-top: 30px;">🗂 Categorized News</h3>
              {self._get_category_section("🏦 Stock News", "#1E40AF", self.categorized_news.get("Stock", []))}
              {self._get_category_section("🌐 Economy News", "#0F766E", self.categorized_news.get("Economy", []))}
              {self._get_category_section("🏛 Policy/Regulation News", "#92400E", self.categorized_news.get("Policy", []))}

              <hr style="border: none; height: 1px; background-color: #E2E8F0; margin: 30px 0;" />
              <p style="font-size: 13px; color: #94A3B8;">
                You're receiving this email because you subscribed to the <strong>Financial News Dashboard</strong>.
                <br>
                <a href="https://your-site.com/unsubscribe" style="color: #EF4444;">Unsubscribe</a> |
                <a href="https://your-site.com" style="color: #3B82F6;">Visit Dashboard</a>
              </p>
            </div>
          </body>
        </html>
        """
        return html
