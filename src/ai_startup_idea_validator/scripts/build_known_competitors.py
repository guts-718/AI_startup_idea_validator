import json
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path


WIKI_PAGES = {
    "fintech": "https://en.wikipedia.org/w/index.php?fulltext=1&search=List+of+fintech+companies&title=Special%3ASearch&ns0=1",
    "saas": "https://en.wikipedia.org/wiki/List_of_software_companies",
}

OUTPUT_PATH = Path("data/known_competitors.json")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_companies(url: str, industry: str):
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    competitors = set()

    # Common Wikipedia patterns
    for a in soup.select("div.mw-parser-output li a"):
        name = clean(a.get_text())

        # basic sanity filters
        if not name:
            continue
        if len(name.split()) > 5:
            continue
        if any(char.isdigit() for char in name):
            continue

        competitors.add(name)

    return [
        {
            "name": name,
            "industry": industry,
            "problem": "industry-specific problem",
            "solution": "industry-specific solution",
            "positioning": "Not specified"
        }
        for name in competitors
    ]



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
