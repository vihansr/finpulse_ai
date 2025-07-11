from bs4 import BeautifulSoup as BS
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class NewsScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Required for GitHub Actions
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.overall_news = []

    def fetch_moneycontrol(self):
        try:
            url = "https://www.moneycontrol.com/news/business/stocks/"
            page = requests.get(url)
            soup = BS(page.content, "html.parser")
            news_items = soup.find_all("li", class_="clearfix")
            for news in news_items:
                self.overall_news.append(news.get_text().strip())
        except Exception as e:
            print("Unable to fetch data from Moneycontrol. Error:", e)

    def fetch_economic_times(self):
        try:
            url = "https://economictimes.indiatimes.com/markets"
            page = requests.get(url)
            soup = BS(page.content, "html.parser")
            news_list = soup.find('ul', class_="newsList")
            if news_list:
                for news in news_list:
                    self.overall_news.append(news.get_text())
        except Exception as e:
            print("Unable to fetch data from Economic Times. Error:", e)

    def fetch_business_standard(self):
        try:
            url = "https://www.business-standard.com/"
            self.driver.get(url)
            news_items = self.driver.find_elements(By.CLASS_NAME, "cardlist")
            for news in news_items:
                cleaned = news.text.strip().replace("\n", "").replace("premium", "")
                for x in ["2 min read", "3 min read", "4 min read", "5 min read"]:
                    cleaned = cleaned.replace(x, "")
                self.overall_news.append(cleaned)
        except Exception as e:
            print("Unable to fetch data from Business Standard. Error:", e)

    def fetch_livemint(self):
        try:
            url = "https://www.livemint.com/latest-news"
            self.driver.get(url)
            news_items = self.driver.find_elements(By.CLASS_NAME, "listingNew")
            for news in news_items:
                self.overall_news.append(news.text.strip().replace("\n", ""))
        except Exception as e:
            print("Unable to fetch data from LiveMint. Error:", e)

    def fetch_cnbc(self):
        try:
            url = "https://www.cnbctv18.com/market/"
            page = requests.get(url)
            soup = BS(page.content, "html.parser")
            news_items = soup.find_all("h3", class_="jsx-f14ac246253a1b7d")
            for news in news_items:
                self.overall_news.append(news.get_text())
        except Exception as e:
            print("Unable to fetch data from CNBC. Error:", e)

    def get_index_data(self):
        try:
            url = "https://finance.yahoo.com/quote/%5ENSEI/"
            self.driver.get(url)
            news_items = self.driver.find_element(By.CLASS_NAME, "yf-ipw1h0")
            print(news_items.text)
        except Exception as e:
            print("Unable to fetch data from LiveMint. Error:", e)

    def get_all_news(self):
        self.fetch_moneycontrol()
        self.fetch_economic_times()
        self.fetch_business_standard()
        self.fetch_livemint()
        self.fetch_cnbc()
        self.driver.quit()
        return self.overall_news