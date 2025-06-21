import plotly.graph_objects as go
from collections import Counter
import streamlit as st

class SentimentPieChart:
    def __init__(self, sentiment_results, include_neutral=False):
        self.sentiment_results = sentiment_results
        self.include_neutral = include_neutral
        self.colors = {
            "positive": "#2ecc71",   # Green
            "negative": "#e74c3c",   # Red
            "neutral": "#BDC3C7"     # Light Gray (Faded)
        }

    def generate(self):
        # Filter labels
        valid_labels = ["positive", "negative"]
        if self.include_neutral:
            valid_labels.append("neutral")

        sentiment_labels = [item['label'].lower() for item in self.sentiment_results if item['label'].lower() in valid_labels]
        counts = Counter(sentiment_labels)

        if not counts:
            st.warning("⚠️ No valid sentiment data to display.")
            return

        labels = list(counts.keys())
        values = list(counts.values())
        colors = [self.colors[label] for label in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textinfo="label+percent",
            insidetextorientation='radial',
            hole=0.4
        )])

        fig.update_layout(
            title_text="",
            title_x=0.5,
            showlegend=True,
            margin=dict(t=40, b=0, l=0, r=0),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)
