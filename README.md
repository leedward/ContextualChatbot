# Contextual Chat and Web Crawling Project

## Project Description
This project is POC that integrates several Python scripts to perform chat analysis and web crawling tasks. It employs advanced natural language processing techniques, leveraging OpenAI's embeddings for contextual understanding, and utilizes a web crawler for gathering text data. The primary components include:

- `chat.py`: Handles chat analysis and context generation using OpenAI's embeddings.
- `endpoint.py`: A Flask-based server that provides endpoints for chat interactions and web crawling.
- `generateEmbedding.py`: Processes text data to create embeddings using OpenAI's API.
- `loadData.py`: Loads embedding data into Redis for efficient retrieval.
- `textToCsv.py`: Processes raw text files, extracting relevant information based on predefined contexts.
- `webcrawler.py`: A script for crawling web pages, extracting text, and storing it for further processing.

## Setup Instructions
1. **Clone the Repository**: Clone this repository to your local machine.

2. **Environment Setup**:
    - Ensure Python is installed.
    - Set up a virtual environment in the project directory: `python -m venv venv`
    - Activate the virtual environment:
        - Windows: `venv\Scripts\activate`
        - Unix or MacOS: `source venv/bin/activate`
    - Install required dependencies: `pip install -r requirements.txt`

3. **Environment Variables**:
    - Create a `.env` file in the project root.
    - Add the OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

4. **Redis Setup**:
    - Ensure Redis is installed and running on your system.
    - The default configuration in the scripts assumes Redis is running locally on the default port (6379).

5. **Data Directory**:
    - Create a `data` directory in the project root for storing processed and scraped data.

6. **Update Prompts**:
   - endpoint.py needs custom prompts in the message, ensure you instruct GPT to only use context provided {context} to answer {question}

6. **Running the Scripts**:
    - Each script can be run independently based on your requirements

## Usage
- **Web Crawling**: Run `webcrawler.py` to start crawling a specified domain.
- **Chat Analysis**: Use `chat.py` for analyzing chat data and generating contexts.
- **Generate Embeddings**: Run `generateEmbedding.py` to process scraped data and generate embeddings.
- **Load Data**: Execute `loadData.py` to load data into Redis.
- **Text Processing**: Run `textToCsv.py` to process raw text files into a structured format.

## Configuring the Web Crawler

To specify websites for the web crawler to start crawling, you have several options:

### 1. Using a Configuration File
Create a `config.json` file in your project's root directory with the following structure:

```json
{
    "start_urls": ["https://example.com", "https://anotherexample.com"]
}
```

Modify `webcrawler.py` to read these URLs:

```python
import json

# Load start URLs from the configuration file
with open('config.json', 'r') as file:
    config = json.load(file)
start_urls = config["start_urls"]

# Use start_urls in your crawl function
for url in start_urls:
    crawl(url)
```

### 2. Using Command-Line Arguments
Use the `argparse` module to accept URLs as command-line arguments. In `webcrawler.py`, add the following:

```python
import argparse

# Setup argument parser
parser = argparse.ArgumentParser(description='Web Crawler')
parser.add_argument('--urls', nargs='+', help='List of starting URLs for the crawler')

# Parse arguments
args = parser.parse_args()
start_urls = args.urls

# Use start_urls in your crawl function
for url in start_urls:
    crawl(url)
```

Run your script from the command line like this:

```bash
python webcrawler.py --urls https://example.com https://anotherexample.com
```

### 3. Hardcoding URLs
Directly define the URLs in your `webcrawler.py` script:

```python
# Define start URLs
start_urls = ["https://example.com", "https://anotherexample.com"]

# Use start_urls in your crawl function
for url in start_urls:
    crawl(url)
```

Choose the method that best suits your project's needs. Using a configuration file or command-line arguments offers more flexibility, while hardcoding is simpler but less adaptable.


## Open Source License
This project is released under the [MIT License](https://opensource.org/licenses/MIT), a permissive open source license. This allows for reuse, modification, and distribution for both private and commercial purposes, provided that the license and copyright notice are included with any substantial portions of the software.
