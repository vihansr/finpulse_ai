from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline, AutoModelForSeq2SeqLM
import torch
import requests
from collections import Counter

class FinancialNewsSentimentAnalyzer:
    def __init__(self, model_name="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipeline = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)

    def analyze(self, news_list):
        results = self.pipeline(news_list)
        output = []

        for i, res in enumerate(results):
            output.append({
                "headline": news_list[i],
                "label": res["label"],
                "score": round(res["score"], 3)
            })

        return output

class HeadlineSelector:
    def __init__(self, model_id="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
        self.model.eval()

        self.labels = ['negative', 'neutral', 'positive']

    def get_sentiment_score(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

        label_idx = torch.argmax(probs).item()
        label = self.labels[label_idx]
        confidence = probs[label_idx].item()

        if label == 'positive':
            impact_score = confidence
        elif label == 'negative':
            impact_score = -confidence
        else:
            impact_score = 0

        return label, confidence, impact_score

    def select_top_10(self, headlines: list[str], top_k: int = 10) -> list[str]:
        scored = []
        for h in headlines:
            label, conf, impact = self.get_sentiment_score(h)
            if impact != 0:
                scored.append((h, impact))

        # Sort by absolute sentiment strength (positive or negative)
        sorted_headlines = sorted(scored, key=lambda x: abs(x[1]), reverse=True)
        top_headlines = [h for h, _ in sorted_headlines[:top_k]]

        return top_headlines

    def select_top_50(self, headlines: list[str], top_k: int = 50) -> list[str]:
        scored = []
        for h in headlines:
            label, conf, impact = self.get_sentiment_score(h)
            if impact != 0:
                scored.append((h, impact))

        # Sort by absolute sentiment strength (positive or negative)
        sorted_headlines = sorted(scored, key=lambda x: abs(x[1]), reverse=True)
        top_headlines = [h for h, _ in sorted_headlines[:top_k]]

        return top_headlines

class StockMentionMapper:
    def __init__(self):
        self.ner = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )

        self.company_to_ticker = {
            "Reliance": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "Infosys": "INFY.NS",
            "RBI": None,
            "HDFC Bank": "HDFCBANK.NS",
            "LIC": "LICI.NS",
            "Adani": "ADANIENT.NS",
            "ICICI Bank": "ICICIBANK.NS",
            "SBI": "SBIN.NS",
            "PTC India": "PTC.NS"
        }

        self.banned_symbols = {
            "^BSESN", "^NSEBANK", "^NSEI", "^NSEMDCP50", "^CNXIT", "FMCGIETF.BO", "0P0000XVLA.BO"
        }

        self.banned_keywords = {
            "Bank", "Sensex", "Index", "FMCG", "ETF", "Mutual Fund", "Government",
            "Sector", "Market", "PSU", "RBI", "Nifty", "India", "Company"
        }

        self.banned_keywords = {"index", "etf", "fund", "benchmark", "sensex", "nifty", "nasdaq", "dow", "s&p", "bse"}

    def _is_probable_index(self, name: str) -> bool:
        return any(kw.lower() in name.lower() for kw in self.banned_keywords)

    def _search_ticker_online(self, name: str):
        if self._is_probable_index(name):
            return None

        try:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={name}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code != 200:
                print(f"[❌] Yahoo search failed for '{name}' — Status: {response.status_code}")
                return None

            data = response.json()
            for result in data.get("quotes", []):
                if result.get("exchange") in ["NSI", "BSE"] and not self._is_probable_index(result.get("shortname", "")):
                    return result["symbol"]

        except Exception as e:
            print(f"[⚠️] Error fetching ticker for '{name}': {e}")
        return None

    def extract_mentions(self, news_list: list) -> list:
        all_orgs = []

        for text in news_list:
            if not text:
                continue
            entities = self.ner(text)
            orgs = [e['word'] for e in entities if e['entity_group'] == 'ORG']
            all_orgs.extend(orgs)

        org_counts = Counter(all_orgs)
        mention_map = {}

        for org, count in org_counts.items():
            cleaned_org = org.lstrip("#").strip()

            if not cleaned_org or len(cleaned_org) < 3:
                continue

            if cleaned_org.lower() in self.banned_keywords:
                continue

            if cleaned_org in mention_map:
                continue

            if cleaned_org in self.banned_symbols:
                continue

            if cleaned_org.lower() in (word.lower() for word in self.banned_keywords):
                continue

            ticker = self.company_to_ticker.get(cleaned_org)
            if ticker is None:
                ticker = self._search_ticker_online(cleaned_org)
                if ticker:
                    self.company_to_ticker[cleaned_org] = ticker

            if ticker:
                mention_map[cleaned_org] = {"ticker": ticker, "count": count}

        sorted_mentions = sorted(mention_map.items(), key=lambda x: x[1]["count"], reverse=True)
        return sorted_mentions


class NewsCategorizer:
    def __init__(self, model_name="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"):
        from transformers import pipeline
        self.categories = ["Market & Stocks", "Economy & Policy", "Global & Industry"]
        self.pipe = pipeline("zero-shot-classification", model=model_name)


    def categorize(self, news_list):
        categorized = {category: [] for category in self.categories}
        assigned = set()

        for headline in news_list:
            if not headline or not headline.strip():
                continue  # Skip empty strings or None

            if headline in assigned:
                continue  # Skip duplicates

            try:
                result = self.pipe(headline, self.categories)
                top_cat = result['labels'][0]
                if top_cat in self.categories:
                    categorized[top_cat].append(headline)
                    assigned.add(headline)
            except Exception as e:
                print(f"⚠️ Skipping headline due to error: {headline}\n{e}")
                continue

        return categorized

