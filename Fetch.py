import sys
import time
import requests
from pathlib import Path

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

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

    sys.stdout.write(f"\r[{bar}] {percent_text} ({current}/{total} URLs downloaded)")
    sys.stdout.flush()

# Simulate downloading URLs from a provided file
if len(sys.argv) < 2:
    print("Usage: python script.py <file_with_urls>")
    sys.exit(1)

file_with_urls = sys.argv[1]

try:
    with open(file_with_urls, 'r') as file:
        urls = [url.strip() for url in file if url.strip()]
        total_urls = len(urls)

        print("Starting downloads...\n")
        for idx, url in enumerate(urls, start=1):
            try:
                print(f"Downloading: {url}")
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Save the file in the current working directory
                filename = url.split("/")[-1] or f"file_{idx}"  # Extract filename or use fallback
                filepath = Path.cwd() / filename
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Saved to: {filepath}")
            except requests.RequestException as e:
                print(f"Error downloading {url}: {e}")

            # Update the progress bar
            display_overall_progress(idx, total_urls)
        
        print("\nAll downloads completed.")
except FileNotFoundError:
    print("File not found. Please provide a valid file with URLs.")
