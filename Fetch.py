import sys
import time
import requests
from pathlib import Path
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;214m"
WHITE_BG = "\033[48;5;255m"  # White background

# Function to display the overall progress bar with color
def display_overall_progress(current, total, bar_length=30):
    progress = int((current / total) * bar_length)
    bar = GREEN + "█" * progress + CYAN + "▒" * (bar_length - progress) + RESET
    percentage = int((current / total) * 100)

    # Add colors to percentage text
    if percentage < 30:
        percent_text = RED + f"{percentage}%" + RESET
    elif percentage < 70:
        percent_text = YELLOW + f"{percentage}%" + RESET
    else:
        percent_text = GREEN + f"{percentage}%" + RESET

    sys.stdout.write(f"\r[{bar}] {percent_text}")
    sys.stdout.flush()

# Function to download content from a URL
def download_url(url, idx, download_dir):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, stream=True, verify=False, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # If the content disposition header is present, use it to determine the filename
        if 'content-disposition' in response.headers:
            filename = response.headers['content-disposition'].split('filename=')[1].strip('"')
        else:
            filename = url.split("/")[-1] or f"file_{idx}"

        filepath = download_dir / filename  # Save to the specified directory
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return GREEN + f"Successfully downloaded: {url} -> {filepath}" + RESET  # Green for success
    except requests.RequestException as e:
        return RED + f"Error: {url} -> {e}" + RESET  # Red for error

# Function to handle URL and wordlist pairing
def process_url_with_wordlist(base_url, wordlist_file, download_dir):
    disable_ssl = input("Disable SSL verification? (yes/no): ").strip().lower() == 'yes'

    try:
        with open(wordlist_file, 'r') as file:
            words = [word.strip() for word in file if word.strip()]
            total_words = len(words)

            print("Starting requests with wordlist...")
            display_overall_progress(0, total_words)

            for idx, word in enumerate(words, start=1):
                constructed_url = f"{base_url}/{word}"
                try:
                    response = requests.get(constructed_url, verify=not disable_ssl, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        log = GREEN + f"Requesting: {WHITE_BG}{constructed_url}{RESET} | Status Code: {response.status_code}" + RESET
                    else:
                        log = RED + f"Requesting: {WHITE_BG}{constructed_url}{RESET} | Status Code: {response.status_code}" + RESET
                except requests.RequestException as e:
                    log = RED + f"Error requesting {WHITE_BG}{constructed_url}{RESET}: {e}" + RESET

                # Print the log and update the progress bar
                print(f"\n{log}")
                display_overall_progress(idx, total_words)

            print("\nAll requests completed.")
    except FileNotFoundError:
        print("Wordlist file not found. Please provide a valid file.")

# Main program
if __name__ == "__main__":
    # Prompt the user for a directory name
    download_dir_name = input("Enter the name for the download directory: ").strip()

    # Create the directory if it doesn't exist
    download_dir = Path.cwd() / download_dir_name
    if not download_dir.exists():
        download_dir.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}Created directory: {download_dir}{RESET}")
    else:
        print(f"{YELLOW}Using existing directory: {download_dir}{RESET}")

    print(f"{YELLOW}Choose an option:{RESET}")
    print("1. Download URLs from a file")
    print("2. Construct URLs with a base URL and wordlist")
    choice = input(f"{CYAN}Enter your choice (1/2): {RESET}").strip()

    if choice == "1":
        file_with_urls = input("Enter the name of the file containing URLs (in the current directory): ").strip()
        filepath = Path.cwd() / file_with_urls

        if not filepath.is_file():
            print("File not found. Please provide a valid file name.")
            sys.exit(1)

        try:
            with open(filepath, 'r') as file:
                urls = [url.strip() for url in file if url.strip()]
                total_urls = len(urls)

                print("\nStarting downloads...")
                display_overall_progress(0, total_urls)

                for idx, url in enumerate(urls, start=1):
                    log = download_url(url, idx, download_dir)
                    print(f"\n{log}")

                    # Update the progress bar
                    display_overall_progress(idx, total_urls)

                print("\nAll downloads completed.")
        except FileNotFoundError:
            print("File not found. Please provide a valid file with URLs.")

    elif choice == "2":
        base_url = input("Enter the base URL: ").strip()
        wordlist_file = input("Enter the name of the wordlist file (in the current directory): ").strip()
        filepath = Path.cwd() / wordlist_file

        if not filepath.is_file():
            print("Wordlist file not found. Please provide a valid file name.")
            sys.exit(1)

        process_url_with_wordlist(base_url, filepath, download_dir)

    else:
        print("Invalid choice. Please restart the program and select a valid option.")
