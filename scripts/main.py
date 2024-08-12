# %%
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
