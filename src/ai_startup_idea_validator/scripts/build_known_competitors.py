import json                    
import requests                 # For making HTTP requests to fetch web pages
from bs4 import BeautifulSoup   # For parsing HTML content
import re                       # For text cleaning using regex
from pathlib import Path      


#  Target Wikipedia Pages
# Mapping of industry → Wikipedia search/list page
WIKI_PAGES = {
    "fintech": "https://en.wikipedia.org/w/index.php?fulltext=1&search=List+of+fintech+companies&title=Special%3ASearch&ns0=1",
    "saas": "https://en.wikipedia.org/wiki/List_of_software_companies",
}

# Output file path where scraped data will be stored
OUTPUT_PATH = Path("data/known_competitors.json")


# Utility: Clean Text 
def clean(text: str) -> str:
    """
    Cleans text by:
    - removing extra whitespace
    - trimming leading/trailing spaces
    """
    return re.sub(r"\s+", " ", text.strip())


# Core Scraper 
def extract_companies(url: str, industry: str):
    """
    Extracts company names from a Wikipedia page
    and formats them into structured competitor objects
    """

    # Fetch page content
    res = requests.get(url, timeout=10)

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(res.text, "html.parser")

    # Use a set to avoid duplicate company names
    competitors = set()

    # Extraction Logic 
    # Select all anchor tags inside list items within main content
    for a in soup.select("div.mw-parser-output li a"):

        # Extract and clean text (company name)
        name = clean(a.get_text())

        #  Filtering (important)

        # Skip empty names
        if not name:
            continue

        # Skip overly long names (likely not company names)
        if len(name.split()) > 5:
            continue

        # Skip names containing numbers (often noise like references, years)
        if any(char.isdigit() for char in name):
            continue

        # Add valid company name to set
        competitors.add(name)

    #  Structuring Output 
    # Convert each company into a structured dictionary
    return [
        {
            "name": name,
            "industry": industry,

            # Placeholder fields (can be improved later using LLMs or APIs)
            "problem": "industry-specific problem",
            "solution": "industry-specific solution",
            "positioning": "Not specified"
        }
        for name in competitors
    ]


#  Main Pipeline 
def main():
    all_competitors = []

    # Loop through each industry and scrape its companies
    for industry, url in WIKI_PAGES.items():
        print(f"Scraping {industry}...")

        # Extract companies for this industry
        comps = extract_companies(url, industry)

        # Add to master list
        all_competitors.extend(comps)

    # Save to File 

    # Ensure the output directory exists
    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    # Write data to JSON file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_competitors, f, indent=2)

    # Log result
    print(f"Saved {len(all_competitors)} competitors to {OUTPUT_PATH}")


# Entry Point 
# Ensures script runs only when executed directly (not imported)
if __name__ == "__main__":
    main()