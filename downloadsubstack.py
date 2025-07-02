import requests
from bs4 import BeautifulSoup
import os
import argparse
import logging
from urllib.parse import urlparse

# Set up basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_post_urls(archive_url: str) -> list:
    """
    Fetches the Substack archive page and extracts all individual post URLs.
    """
    logging.info(f"Fetching post URLs from: {archive_url}")
    try:
        response = requests.get(archive_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch archive page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    post_links = sorted(list(
        set([link for link in links if '/p/' in link and link.startswith('https://')])))
    logging.info(f"Found {len(post_links)} post links.")
    return post_links


def download_post_html(post_url: str, output_dir: str):
    """
    Downloads a single post as a self-contained HTML file by adding a <base> tag.
    """
    try:
        url_path = urlparse(post_url).path
        file_name = f"{url_path.strip('/').split('/')[-1]}.html"
        file_path = os.path.join(output_dir, file_name)

        logging.info(f"Downloading {post_url} -> {file_path}")
        response = requests.get(post_url, timeout=30)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the <head> section
        head = soup.head

        # If the <head> tag exists, add a <base> tag to it
        if head:
            base_tag = soup.new_tag('base', href=post_url)
            head.insert(0, base_tag)  # Insert it at the beginning of the head

        # Save the modified HTML
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        logging.info(f"Successfully saved {file_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to download {post_url}. Reason: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download all posts from a Substack archive as HTML files.")
    parser.add_argument(
        "url", help="The URL of the Substack archive (e.g., 'https://yourname.substack.com/archive')")
    parser.add_argument("-o", "--output", default="substack_posts",
                        help="The directory where HTML files will be saved. Defaults to 'substack_posts'.")
    args = parser.parse_args()

    post_urls = get_post_urls(args.url)
    if not post_urls:
        logging.warning("No post URLs found. Exiting.")
        return

    substack_name = urlparse(args.url).netloc.split('.')[0]
    output_directory = os.path.join(args.output, substack_name)
    os.makedirs(output_directory, exist_ok=True)
    logging.info(f"Saving HTML files to: {output_directory}")

    success_count = 0
    failure_count = 0
    for i, url in enumerate(post_urls):
        print("-" * 20)
        logging.info(f"Processing post {i+1} of {len(post_urls)}")
        if download_post_html(url, output_directory):
            success_count += 1
        else:
            failure_count += 1
    print("=" * 20)
    logging.info("Download complete.")
    logging.info(f"Successful downloads: {success_count}")
    logging.info(f"Failed downloads: {failure_count}")


if __name__ == "__main__":
    main()
