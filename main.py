from transformers import pipeline
from bs4 import BeautifulSoup
import requests

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

# Function to get search results from DuckDuckGo
def search_duckduckgo(query, num_results=3):
    search_url = "https://duckduckgo.com/html/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch the search page")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for link in soup.select("a.result__a")[:num_results]:
        title = link.get_text()
        url = link["href"]
        results.append({"title": title, "url": url})

    return results

# Function to extract paragraphs from a webpage
def get_paragraphs_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch content from {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    return paragraphs

# Function to summarize text into three paragraphs
def summarize_text(paragraphs, url):
    # Join paragraphs into one text and summarize in parts
    text = " ".join(paragraphs[:10])  # Limit to 10 paragraphs to avoid too much text
    summary_parts = []

    # Summarize text in chunks of 512 tokens each to keep within model limits
    for i in range(0, len(text), 512):
        chunk = text[i:i+512]
        summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        summary_parts.append(summary)

    # Combine summaries into three paragraphs
    combined_summary = "\n\n".join(summary_parts[:3])  # Ensure we only take the first 3 parts

    # Append URL to indicate source
    return f"{combined_summary}\n\nSource: {url}"

# Example usage
query = "Python web scraping"
search_results = search_duckduckgo(query)

# Summarize and display results for the first 3 URLs
for result in search_results:
    title = result['title']
    url = result['url']
    paragraphs = get_paragraphs_from_url(url)

    if paragraphs:
        summary = summarize_text(paragraphs, url)
        print(f"Title: {title}\n")
        print(f"Summary:\n{summary}")
        print("\n" + "="*60 + "\n")
