import json
from model import NewsCategorizer, FinancialNewsSentimentAnalyzer, HeadlineSelector, StockMentionMapper
from news import NewsScraper
from datetime import datetime
import json
import glob
import os

for f in glob.glob("preprocessed_*.json"):
    os.remove(f)

# Use today's date for output filename
today_str = datetime.now().strftime("%Y-%m-%d")
output_file = f"preprocessed_{today_str}.json"

# 1. 📰 Scrape News
scraper = NewsScraper()
news_list = scraper.get_all_news()

# 2. 😊 Sentiment Analysis
sentiment_analyzer = FinancialNewsSentimentAnalyzer()
sentiment_results = sentiment_analyzer.analyze(news_list)

# 3. 🗂️ Categorization
categorizer = NewsCategorizer()
categorized_news = categorizer.categorize(news_list)

# 4. 🌟 Top Headlines
selector = HeadlineSelector()
top_headlines = selector.select_top_10(news_list)

# 5. 📌 Top Mentioned Stocks
mapper = StockMentionMapper()
stock_mentions = mapper.extract_mentions(news_list, top_n=5)

# 6. 💾 Save everything to JSON
data = {
    "news": news_list,
    "sentiment": sentiment_results,
    "categories": categorized_news,
    "top_headlines": top_headlines,
    "stock_mentions": stock_mentions
}

with open(output_file, "w", encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Preprocessing complete and saved to", output_file)
