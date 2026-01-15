import json
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path


WIKI_PAGES = {
    "fintech": "https://en.wikipedia.org/wiki/List_of_fintech_companies",
    "saas": "https://en.wikipedia.org/wiki/List_of_software_companies",
}

OUTPUT_PATH = Path("data/known_competitors.json")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_companies(url: str, industry: str):
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    competitors = []

    for li in soup.select("li"):
        name = clean(li.get_text())
        if len(name.split()) > 8 or len(name) < 3:
            continue

        competitors.append({
            "name": name,
            "industry": industry,
            "problem": "industry-specific problem",
            "solution": "industry-specific solution",
            "positioning": "Not specified"
        })

    return competitors


def main():
    all_competitors = []

    for industry, url in WIKI_PAGES.items():
        print(f"Scraping {industry}...")
        comps = extract_companies(url, industry)
        all_competitors.extend(comps)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_competitors, f, indent=2)

    print(f"Saved {len(all_competitors)} competitors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
