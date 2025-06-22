import streamlit as st
import plotly.express as px
from collections import Counter
from database import add_subscriber, create_table
from mail import WelcomeEmailSender
from model import NewsCategorizer, FinancialNewsSentimentAnalyzer, HeadlineSelector, StockMentionMapper
from news import NewsScraper

# Page Config
st.set_page_config(page_title="📈 Financial Dashboard", layout="wide")

# Create DB Table
create_table()

# -------------------- Cached Data Loader --------------------
@st.cache_data(show_spinner="📡 Fetching and analyzing news...")
def load_data():
    scraper = NewsScraper()
    news_list = scraper.get_all_news()

    sentiment_analyzer = FinancialNewsSentimentAnalyzer()
    sentiment_results = sentiment_analyzer.analyze(news_list)

    categorizer = NewsCategorizer()
    categorized_news = categorizer.categorize(news_list)

    selector = HeadlineSelector()
    top_headlines = selector.select_top_10(news_list)

    mapper = StockMentionMapper()
    stock_mentions = mapper.extract_mentions(news_list)

    return {
        "news": news_list,
        "sentiment": sentiment_results,
        "top_headlines": top_headlines,
        "stock_mentions": stock_mentions,
        "categorized_news": categorized_news,
    }

data = load_data()
mock_headlines = data["top_headlines"]
mock_sentiments = data["sentiment"]
stock_mentions = data.get("stock_mentions", [])

# -------------------- Stock Ticker Marquee --------------------
def render_stock_ticker(stock_mentions):
    if not stock_mentions:
        return

    # Create a continuous scrolling string
    scrolling_text = " ".join(
        [f"💹 <b>{name}</b> ({info['ticker']})" for name, info in stock_mentions]
    )

    full_text = scrolling_text + scrolling_text  # repeat for seamless loop

    st.markdown(f"""
        <div style="
            width: 100%;
            padding: 10px 0;
            margin-bottom: 25px;
            font-size: 16px;
            font-weight: 600;
            overflow: hidden;
            color: white;
        ">
            <marquee behavior="scroll" direction="left" scrollamount="4" loop="infinite">
                {full_text}
            </marquee>
        </div>
    """, unsafe_allow_html=True)


render_stock_ticker(stock_mentions)

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
                    st.success(f"✅ Subscribed! Welcome email sent to {email_input}")
                    sender = WelcomeEmailSender()
                    sender.send_welcome_email(email_input)
                else:
                    st.info("You're already subscribed.")
            else:
                st.error("❌ Please enter a valid email address.")

st.markdown("---")

# -------------------- Sentiment Pie Chart --------------------
st.subheader("📊 Sentiment Distribution")

# Filter out 'neutral' entries
filtered_sentiments = [item['label'].capitalize() for item in mock_sentiments if item['label'].lower() != "neutral"]
sentiment_counts = Counter(filtered_sentiments)

fig = px.pie(
    names=list(sentiment_counts.keys()),
    values=list(sentiment_counts.values()),
    color=list(sentiment_counts.keys()),
    color_discrete_map={
        "Positive": "#4CAF50",
        "Negative": "#F44336"
    },
    title="Sentiment Breakdown",
    hole=0.45
)
fig.update_traces(textinfo="label+percent", textfont_size=14, pull=[0.03]*len(sentiment_counts))

st.plotly_chart(fig, use_container_width=True)


# -------------------- Top 10 Headlines --------------------
st.subheader("🔥 Top 10 Headlines")
for idx, headline in enumerate(mock_headlines, start=1):
    st.markdown(f"""
    <div style='
        padding: 12px;
        background-color: #e8f0fe;
        color: #1a1a1a;
        border-left: 5px solid #1a73e8;
        margin-bottom: 10px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 500;
    '>
        <span style="color: #1a73e8;">{idx}.</span> {headline}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------- Footer --------------------
st.markdown("<p style='text-align:center; color:gray;'>🧠 Built with Streamlit • Live insights powered by Transformers</p>", unsafe_allow_html=True)
