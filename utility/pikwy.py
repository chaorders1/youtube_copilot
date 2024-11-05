"""Pikwy Screenshot Utility

This module provides functionality to capture YouTube channel screenshots using the Pikwy API.
It saves screenshots to a specified output directory with configurable options.

Example Usage:
    # Basic usage - capture single URL screenshot
    pikwy_screenshot('https://www.youtube.com/@anthropic-ai/featured')
    
    # Capture with custom options
    pikwy_screenshot('https://www.youtube.com/@anthropic-ai/featured',
                    width=1920,
                    format='jpg',
                    output_dir='screenshots')
    
    # Command line usage:
    # Capture single URL:
    # python pikwy.py --url='https://www.youtube.com/@anthropic-ai/featured'
    # Capture video tab URL:
    # python pikwy.py --url='https://www.youtube.com/@anthropic-ai/videos'
    
    # Capture multiple URLs from file:
    # python pikwy.py --file='urls.txt'

Features:
    - Captures full page or partial screenshots
    - Configurable viewport width and format
    - Custom delay for dynamic content loading
    - Progress tracking and logging
    - Organized output directory structure
    - Error handling and retries

Output Structure:
    data/pikwy_screenshots/
    ├── anthropic-ai/             # Screenshot folder per channel
    └── pikwy_screenshot.png      # Screenshot file

Requirements:
    - Python 3.6+
    - urllib (standard library)
    - os (standard library)
    - python-dotenv (optional, for environment variables)

Notes:
    - Screenshots saved to 'data/pikwy_screenshots' by default
    - Supports PNG and JPG formats
    - Configurable viewport width (default 1280px)
    - Adjustable delay for content loading
    - Handles authentication via API token
"""

#!/usr/bin/python3
import urllib.request
import urllib.parse
import os
import argparse
from dotenv import load_dotenv

def generate_screenshot_api_url(token, options):
  api_url = 'https://api.pikwy.com/?token=' + token
  if token:
    api_url += '&url=' + options.get('url', '')
    api_url += '&width=' + options.get('width', '1280')
    api_url += '&response_type=' + options.get('response_type', 'raw')
    api_url += '&full_page=' + options.get('full_page', '0')
    api_url += '&format=' + options.get('format', 'png')
    api_url += '&delay=' + options.get('delay', '10000')  # Wait 10 seconds
  return api_url

def read_urls_from_file(file_path: str) -> list:
    """
    Read URLs from a file.

    Args:
        file_path (str): The path to the file containing URLs.

    Returns:
        list: A list of URLs.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def save_screenshot(api_url: str, output_path: str) -> None:
    """
    Save a screenshot from the API URL to the specified output path.

    Args:
        api_url (str): The API URL to retrieve the screenshot.
        output_path (str): The path to save the screenshot.
    """
    urllib.request.urlretrieve(api_url, output_path)

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API token from environment variables
    token = os.getenv('PIKWY_API_TOKEN')
    if not token:
        raise ValueError("PIKWY_API_TOKEN not found in environment variables")

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Capture website screenshots using Pikwy API')
    parser.add_argument('--url', help='Single URL to capture')
    parser.add_argument('--file', help='File containing URLs to capture', default='blank.txt')
    args = parser.parse_args()

    options = {
        'width': '1280',
        'height': '2048',
        'response_type': 'image',
        #'full_page': '1',
        'format': 'png',
        'delay': '10000'
    }

    data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data')
    output_dir = os.path.join(data_folder, 'web_snapshots')
    os.makedirs(output_dir, exist_ok=True)

    if args.url:
        # Handle single URL from command line
        options['url'] = args.url
        api_url = generate_screenshot_api_url(token, options)
        output_path = os.path.join(output_dir, f"{urllib.parse.quote(args.url, safe='')}.png")
        save_screenshot(api_url, output_path)
        print(f"Saved screenshot for {args.url} to {output_path}")
    else:
        # Handle URLs from file
        urls_file_path = os.path.join(data_folder, args.file)
        urls = read_urls_from_file(urls_file_path)
        
        for url in urls:
            options['url'] = url
            api_url = generate_screenshot_api_url(token, options)
            output_path = os.path.join(output_dir, f"{urllib.parse.quote(url, safe='')}.png")
            save_screenshot(api_url, output_path)
            print(f"Saved screenshot for {url} to {output_path}")

if __name__ == "__main__":
    main()