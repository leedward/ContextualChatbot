import hashlib
import os
import re
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.parse import urlparse
import PyPDF2
from docx import Document
from io import BytesIO
import requests
from bs4 import BeautifulSoup

# Configurations
DATA_DIR = "data"
TEXT_DIR = os.path.join(DATA_DIR, "text")
EXTERNAL_LINKS_DIR = os.path.join(DATA_DIR, "external-links")
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]*://.+'


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hyperlinks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "href" in attrs:
            if "#" not in attrs["href"]:
                self.hyperlinks.append(attrs["href"])


def get_hyperlinks(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if not response.headers.get('Content-Type').startswith("text/html"):
            return []

        html = response.text
    except Exception as e:
        print(e)
        return []

    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


def get_domain_hyperlinks(local_domain, base_path, url, external_links_set):
    clean_links = []

    for link in set(get_hyperlinks(url)):
        clean_link = None

        if link.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
            continue

        if re.search(HTTP_URL_PATTERN, link):
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain and url_obj.path.startswith(base_path):
                clean_link = link
            else:
                external_links_set.add(url_obj.scheme + '://' + url_obj.netloc)
        else:
            if link.startswith("/"):
                if link.startswith(base_path):
                    clean_link = urljoin("https://" + local_domain, link)
            elif link.startswith("#") or link.startswith("mailto:"):
                continue

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    return list(set(clean_links))


def crawl(url):
    url_obj = urlparse(url)
    local_domain = url_obj.netloc
    base_path = url_obj.path

    queue = deque([url])
    seen = set([url])
    external_links_set = set()

    if not os.path.exists(TEXT_DIR):
        os.mkdir(TEXT_DIR)

    domain_text_dir = os.path.join(TEXT_DIR, local_domain)
    if not os.path.exists(domain_text_dir):
        os.mkdir(domain_text_dir)

    while queue:
        url = queue.pop()
        print(url)

        url_hash = hashlib.sha256(url.encode()).hexdigest()

        try:
            if url.lower().endswith('.pdf'):
                response = requests.get(url)
                pdf_file = PyPDF2.PdfFileReader(BytesIO(response.content))
                text = ''
                for page in range(pdf_file.getNumPages()):
                    text += pdf_file.getPage(page).extract_text()

            elif url.lower().endswith('.docx'):
                response = requests.get(url)
                document = Document(BytesIO(response.content))
                text = '\n'.join([para.text for para in document.paragraphs])

            else:
                soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
                text = soup.get_text()

            with open(os.path.join(domain_text_dir, url_hash + ".txt"), "w", encoding="UTF-8") as f:
                f.write(text)

        except Exception as e:
            print(f"Failed to process {url}. Reason: {str(e)}")

        for link in get_domain_hyperlinks(local_domain, base_path, url, external_links_set):
            if link not in seen:
                queue.append(link)
                seen.add(link)

    if not os.path.exists(EXTERNAL_LINKS_DIR):
        os.mkdir(EXTERNAL_LINKS_DIR)

    with open(os.path.join(EXTERNAL_LINKS_DIR, local_domain + "_external_links.txt"), "w", encoding="UTF-8") as f:
        for external_link in external_links_set:
            f.write(external_link + "\n")
