import requests
from urllib.parse import urlparse
import re
import logging
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def get_urls_from_source(url, session):
    """Fetch and parse URLs from a given sitemap URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }

        response = session.get(url, headers=headers)
        response.raise_for_status()
        content = response.text
        domain = get_domain(url)

        # Try extracting URLs from XML <loc> tags
        urls = re.findall(r'<loc>(.*?)<\/loc>', content)
        
        # If no XML URLs found, try finding all href links in HTML
        if not urls:
            urls = re.findall(r'href=["\'](.*?)["\']', content, re.IGNORECASE)
            # Convert relative URLs to absolute URLs
            urls = [url if url.startswith("http") else f"{domain}/{url.lstrip('/')}" for url in urls]

        # Filter out unwanted URLs
        filtered_urls = []
        for u in urls:
            if (
                "javascript:void(0)" in u or
                u.endswith("#") or
                "?" in u  # General filter for URLs with parameters
            ):
                continue
            filtered_urls.append(u.strip())

        # Remove duplicates
        return list(set(filtered_urls))

    except requests.RequestException as e:
        logging.error(f"Error fetching URLs from {url}: {e}")
        return []

def extract_sitemaps_from_index(sitemap_index_url, session):
    """Extract individual sitemap URLs from a sitemap index."""
    try:
        response = session.get(sitemap_index_url)
        response.raise_for_status()

        # Find all sitemap locations within the <sitemapindex>
        return re.findall(r'<loc>\s*(https?://.*?sitemap[^<]*\.xml)\s*</loc>', response.text, re.IGNORECASE)

    except requests.RequestException as e:
        logging.error(f"Error fetching sitemap index {sitemap_index_url}: {e}")
        return []

def filter_urls_by_domain(domain, urls):
    """Filter URLs to keep only those that match the specified domain."""
    return [url for url in urls if domain in url]

def filter_in_files(urls):
    """Filter URLs based on file extensions, excluding .xml URLs."""
    include_extensions = ('.asp', '.aspx', '.cgi', '.htm', '.html', '.js', '.jsp', '.php', '.py', '')
    exclude_extensions = ('.xml')
    return [url for url in urls if url.lower().endswith(include_extensions) and not url.lower().endswith(exclude_extensions)]

def write_to_file(unique_urls, filename="mappedsites.txt"):
    """Write the list of URLs to a file."""
    with open(filename, "a") as file:
        for url in unique_urls:
            file.write(url + "\n")

def search_for_sitemap_in_robots(domain, session):
    """Search for the sitemap URL in the robots.txt file."""
    robots_url = get_domain(domain) + '/robots.txt'
    try:
        response = session.get(robots_url)
        response.raise_for_status()

        # Extract Sitemap URLs from robots.txt
        sitemap_urls = re.findall(r'Sitemap:\s*(https?://\S+)', response.text, re.IGNORECASE)
        if sitemap_urls:
            logging.info(f"Sitemap found in robots.txt: {sitemap_urls[0]}")
            return sitemap_urls[0]
    except requests.RequestException:
        logging.warning("Failed to fetch robots.txt or no Sitemap found.")
    
    return None

def search_for_sitemap(domain, session):
    """Search for a sitemap by checking default locations or robots.txt."""
    base_url = get_domain(domain)
    initial_sitemap_url = f"{base_url}/sitemap.xml"

    try:
        response = session.get(initial_sitemap_url)
        response.raise_for_status()
        logging.info(f"Sitemap found at: {initial_sitemap_url}")
        return initial_sitemap_url
    except requests.RequestException:
        logging.info("Main sitemap not found. Checking robots.txt...")
        return search_for_sitemap_in_robots(domain, session)

def process_sitemaps_iteratively(starting_sitemap, session):
    """Iteratively process sitemaps to handle nested sitemaps."""
    all_urls = set()
    processed_sitemaps = set()
    sitemap_queue = Queue()

    # Start with the initial sitemap
    sitemap_queue.put(starting_sitemap)

    while not sitemap_queue.empty():
        current_sitemap = sitemap_queue.get()

        if current_sitemap in processed_sitemaps:
            continue  # Avoid reprocessing the same sitemap

        logging.info(f"Processing sitemap: {current_sitemap}")
        processed_sitemaps.add(current_sitemap)

        # Get URLs from the current sitemap
        urls = get_urls_from_source(current_sitemap, session)
        all_urls.update(urls)

        # Check if there are nested sitemaps within the current sitemap
        nested_sitemaps = extract_sitemaps_from_index(current_sitemap, session)
        for nested_sitemap_url in nested_sitemaps:
            if nested_sitemap_url not in processed_sitemaps:
                sitemap_queue.put(nested_sitemap_url)

        # Periodically write to file to avoid memory overflow, had some problems with insanely big websites...
        if len(all_urls) > 1000:
            # Filter the URLs by domain and file type
            filtered_urls = filter_in_files(filter_urls_by_domain(get_domain(starting_sitemap), all_urls))
            write_to_file(filtered_urls)
            all_urls.clear()  # Clear memory after writing to file

    # Write any remaining URLs to file
    if all_urls:
        filtered_urls = filter_in_files(filter_urls_by_domain(get_domain(starting_sitemap), all_urls))
        write_to_file(filtered_urls)

if __name__ == "__main__":
    with requests.Session() as session:
        # Get user input and choose the input method for the sitemap URL
        input_url = input("Enter the sitemap URL or domain: ").strip()
        input_domain = get_domain(input_url)

        # Determine whether the input is a sitemap or a domain
        if input_url.endswith(".xml"):
            sitemap_url = input_url
        else:
            sitemap_url = search_for_sitemap(input_url, session)

        if sitemap_url:
            # Iteratively process the sitemaps to gather all URLs and write directly to "mappedsites.txt"
            process_sitemaps_iteratively(sitemap_url, session)
            logging.info("Mapped sites written to 'mappedsites.txt'")
        else:
            logging.error("Sitemap URL could not be determined.")
