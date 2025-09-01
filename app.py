import feedparser
import pandas as pd
import plotly.express as px
import tldextract
import streamlit as st
from datetime import datetime

# ----------------------------
# 1. App Title
# ----------------------------
st.set_page_config(page_title="Rubber Export Disruption Dashboard", layout="wide")
st.title("🌍 Rubber Export Disruption Dashboard")
st.markdown("Monitoring **rubber market disruption news** in real-time.")

# ----------------------------
# 2. Fetch RSS Feed
# ----------------------------
@st.cache_data(ttl=1800)  # refresh every 30 min
def fetch_news():
    rss_url = "https://news.google.com/rss/search?q=rubber+export+disruption+OR+rubber+tariff+OR+rubber+shortage"
    feed = feedparser.parse(rss_url)
    
    keywords = ["tariff", "ban", "strike", "disruption", "policy"]
    countries = ["Thailand", "Indonesia", "Malaysia", "Vietnam", "India", "Sri Lanka", "China", "Philippines"]
    region_map = {
        "Thailand": "Asia", "Indonesia": "Asia", "Malaysia": "Asia", "Vietnam": "Asia",
        "India": "Asia", "Sri Lanka": "Asia", "China": "Asia", "Philippines": "Asia", "Unknown": "Other"
    }
    domain_country_map = {
        "indiatimes": "India", "bangkokpost": "Thailand", "jakartapost": "Indonesia",
        "thestar": "Malaysia", "chinadaily": "China", "philstar": "Philippines"
    }

    data = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        published = entry.published if 'published' in entry else None
        risk = "High" if any(word.lower() in title.lower() for word in keywords) else "Normal"

        detected_country = "Unknown"
        for c in countries:
            if c.lower() in title.lower():
                detected_country = c
                break
        if detected_country == "Unknown":
            domain = tldextract.extract(link).domain
            detected_country = domain_country_map.get(domain, "Unknown")

        region = region_map.get(detected_country, "Other")
        data.append([title, link, published, risk, detected_country, region])
    
    df = pd.DataFrame(data, columns=["Title", "Link", "Published", "Risk", "Country", "Region"])
    return df

df = fetch_news()

# ----------------------------
# 3. Filters
# ----------------------------
col1, col2 = st.columns(2)
risk_filter = col1.selectbox("Filter by Risk", ["All"] + df["Risk"].unique().tolist())
country_filter = col2.selectbox("Filter by Country", ["All"] + df["Country"].unique().tolist())

filtered_df = df.copy()
if risk_filter != "All":
    filtered_df = filtered_df[filtered_df["Risk"] == risk_filter]
if country_filter != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country_filter]

# ----------------------------
# 4. Visualizations
# ----------------------------
st.subheader("📊 Risk & Regional Overview")

col3, col4 = st.columns(2)
with col3:
    risk_chart = px.bar(df.groupby("Risk").size().reset_index(name="Count"), x="Risk", y="Count",
                        title="News Risk Summary", color="Risk")
    st.plotly_chart(risk_chart, use_container_width=True)

with col4:
    region_chart = px.pie(df, names="Region", title="News by Region")
    st.plotly_chart(region_chart, use_container_width=True)

country_chart = px.bar(df.groupby("Country").size().reset_index(name="Count"), x="Country", y="Count",
                       title="News by Country", color="Country")
st.plotly_chart(country_chart, use_container_width=True)

# ----------------------------
# 5. News Table with Clickable Links
# ----------------------------
st.subheader("📰 Latest Rubber Export Disruption News")
for _, row in filtered_df.iterrows():
    st.markdown(f"**[{row['Title']}]({row['Link']})**  \n"
                f"*Published:* {row['Published']} | *Risk:* {row['Risk']} | *Country:* {row['Country']}")
    st.write("---")
