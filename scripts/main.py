# %%
import datetime
import os
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


def get_report_links() -> list[str]:
    # URL of the RSS feed
    url = "https://edoc.rki.de/feed/rss_2.0/176904/11665"

    # Send a GET request to the RSS feed URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the XML from the response
    root = ET.fromstring(response.content)

    # Extract all the link elements within item elements
    links = [item.find("link").text for item in root.findall(".//item")]

    return links


# This should work for any date, so don't hard code date
def get_file_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    # Extract the href attribute of the first a element within the div with the class ds-artifact
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the URL from the 'citation_pdf_url' meta tag
    url_tag = soup.find("meta", attrs={"name": "citation_pdf_url"})
    if url_tag and url_tag.has_attr("content"):
        pdf_url = url_tag["content"]
        return pdf_url
    else:
        print("PDF URL not found.")


file_urls = [get_file_url(link) for link in get_report_links()]

# Create the data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

for url in file_urls:
    filename = os.path.basename(url)
    filepath = os.path.join("data", filename)

    response = requests.get(url)
    response.raise_for_status()

    with open(filepath, "wb") as file:
        file.write(response.content)

#%%
# Separate the English and German file URLs based on the filename
english_file_urls = [url for url in file_urls if "_EN_" in os.path.basename(url)]
german_file_urls = [url for url in file_urls if "_EN_" not in os.path.basename(url)]

# Create a simple index.html file with links to the downloaded PDFs
with open("index.html", "w") as file:
    file.write("""
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; color: #333; line-height: 1.6; }
            h1 { color: #2c3e50; font-size: 24px; }
            h2 { color: #2c3e50; font-size: 20px; }
            p { font-size: 16px; }
            a { text-decoration: none; color: #3498db; }
            a:hover { color: #2980b9; }
            .report-section { margin-bottom: 40px; }
            .report-list { margin-left: 20px; }
            .container { max-width: 800px; margin: auto; }
        </style>
        <title>RKI Abwasser Reports Mirror</title>
    </head>
    <body>
        <div class="container">
            <h1>RKI Abwasser Reports Mirror</h1>
            <p>This website serves as a mirror for the Robert Koch Institute (RKI) wastewater reports, allowing direct access to the latest reports without requiring file downloads. You can browse the available English and German reports below.</p>
            <p>The original reports are available at <a href="https://edoc.rki.de/handle/176904/11665">https://edoc.rki.de/handle/176904/11665</a>.</p>
            
            <div class="report-section">
                <h2>English Reports</h2>
                <div class="report-list">
    """)
    
    for url in english_file_urls:
        filename = os.path.basename(url)
        file.write(f'<a href="data/{filename}">{filename}</a><br>')
    
    file.write("""
                </div>
            </div>
            <div class="report-section">
                <h2>German Reports</h2>
                <div class="report-list">
    """)
    
    for url in german_file_urls:
        filename = os.path.basename(url)
        file.write(f'<a href="data/{filename}">{filename}</a><br>')
    
    file.write(f"""
                </div>
            </div>
            <p>Created by <a href="https://github.com/corneliusroemer">Cornelius Roemer</a><br>
            Source code available on <a href="https://github.com/corneliusroemer/rki-abwasser-reports">GitHub</a><br>
            Last updated: {datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S %Z")}</p>
        </div>
    </body>
    </html>
    """)
# %%
