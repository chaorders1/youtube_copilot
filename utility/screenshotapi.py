"""Screenshot Utility

This module provides functionality to capture website screenshots using the ScreenshotAPI service.
It saves screenshots to a specified output directory with configurable options.

Example Usage:
    # Basic usage - capture single URL screenshot
    screenshot('https://www.youtube.com/@anthropic-ai/featured')
    
    # Capture with custom options
    screenshot('https://www.youtube.com/@anthropic-ai/featured',
              width=1920,
              format='png',
              output_dir='screenshots')
    
    # Command line usage:
    # Capture single URL:
    # python screenshotapi.py --url='https://www.youtube.com/@anthropic-ai/featured'
    # python screenshotapi.py --url='https://www.youtube.com/@veritasium'
    
    # Capture multiple URLs from file:
    # python screenshotapi.py --file='urls.txt'
    # python screenshotapi.py --file='/path/to/youtube_url.txt'

Features:
    - Captures full page or partial screenshots
    - Configurable viewport dimensions
    - Multiple output formats (PNG, JPG, WebP, PDF)
    - Custom delay for dynamic content loading
    - Progress tracking and logging
    - Error handling and retries
    - Cookie and ad blocking options

Output Structure:
    data/web_snapshots/
    └── screenshot_{timestamp}.png      # Screenshot file

Requirements:
    - Python 3.6+
    - urllib (standard library)
    - os (standard library)
    - python-dotenv (for environment variables)
"""

#!/usr/bin/python3
import urllib.request
import urllib.parse
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenshotAPI:
    """Handles screenshot capture using ScreenshotAPI service."""
    
    BASE_URL = "https://shot.screenshotapi.net/screenshot"
    
    def __init__(self, api_token: str):
        """Initialize with API token."""
        self.api_token = api_token
        
    def generate_api_url(self, url: str, options: Dict) -> str:
        """Generate API URL with parameters."""
        params = {
            'token': self.api_token,
            'url': url,
            'width': options.get('width', '1680'),
            'height': options.get('height', '867'),
            'output': options.get('output', 'image'),
            'file_type': options.get('file_type', 'png'),
            'full_page': options.get('full_page', 'false'),
            'delay': options.get('delay', '5000'),  # 5 second delay
            'block_ads': options.get('block_ads', 'true'),
            'no_cookie_banners': options.get('no_cookie_banners', 'true'),
            'retina': options.get('retina', 'false'),
            'fresh': options.get('fresh', 'true')
        }
        
        # Add optional parameters if specified
        if options.get('css'):
            params['css'] = options['css']
        if options.get('user_agent'):
            params['user_agent'] = options['user_agent']
            
        # Construct query string
        query_string = urllib.parse.urlencode(params)
        return f"{self.BASE_URL}?{query_string}"

def is_valid_url(url: str) -> bool:
    """Validate if the string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def read_urls_from_file(file_path: str) -> List[str]:
    """Read URLs from a file, skipping invalid URLs."""
    valid_urls = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                url = line.strip()
                if url and is_valid_url(url):
                    valid_urls.append(url)
                elif url:
                    logger.warning(f"Skipping invalid URL: {url}")
    except Exception as e:
        logger.error(f"Error reading URLs file: {e}")
        raise
    return valid_urls

def save_screenshot(api_url: str, output_path: str, retries: int = 3) -> bool:
    """
    Save a screenshot from the API URL to the specified output path.
    
    Args:
        api_url: The API URL to retrieve the screenshot
        output_path: The path to save the screenshot
        retries: Number of retry attempts (default: 3)
        
    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(retries):
        try:
            urllib.request.urlretrieve(api_url, output_path)
            logger.info(f"Screenshot saved successfully to: {output_path}")
            return True
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed. Retrying... Error: {e}")
            else:
                logger.error(f"Failed to save screenshot after {retries} attempts: {e}")
                return False
    return False

def capture_screenshot(url: str, output_dir: str, options: Optional[Dict] = None) -> Optional[str]:
    """
    Capture a screenshot of the specified URL.
    
    Args:
        url: The URL to capture
        output_dir: Directory to save the screenshot
        options: Screenshot options
        
    Returns:
        Optional[str]: Path to saved screenshot if successful, None otherwise
    """
    if not options:
        options = {}
        
    try:
        # Initialize API client
        api_token = os.getenv('SCREENSHOT_API_TOKEN')
        if not api_token:
            raise ValueError("SCREENSHOT_API_TOKEN not found in environment variables")
            
        api_client = ScreenshotAPI(api_token)
        
        # Generate API URL
        api_url = api_client.generate_api_url(url, options)
        
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.{options.get('file_type', 'png')}"
        output_path = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save screenshot
        if save_screenshot(api_url, output_path):
            return output_path
            
    except Exception as e:
        logger.error(f"Error capturing screenshot for {url}: {e}")
        
    return None

def main():
    """Main function to handle command line arguments and capture screenshots."""
    # Load environment variables
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Capture website screenshots using ScreenshotAPI')
    parser.add_argument('--url', help='Single URL to capture')
    parser.add_argument('--file', help='File containing URLs to capture')
    parser.add_argument('--width', help='Viewport width', default='1680')
    parser.add_argument('--height', help='Viewport height', default='867')
    parser.add_argument('--format', help='Output format (png/jpg/pdf)', default='png')
    parser.add_argument('--full-page', help='Capture full page', action='store_true')
    args = parser.parse_args()

    # Set up screenshot options
    options = {
        'width': args.width,
        'height': args.height,
        'file_type': args.format,
        'full_page': str(args.full_page).lower(),
        'block_ads': 'true',
        'no_cookie_banners': 'true'
    }

    # Set up output directory
    data_folder = Path(__file__).parent.parent / 'data'
    output_dir = data_folder / 'web_snapshots'
    
    if args.url:
        # Handle single URL
        if output_path := capture_screenshot(args.url, output_dir, options):
            logger.info(f"Screenshot saved to: {output_path}")
    elif args.file:
        # Handle URLs from file
        urls_file = data_folder / args.file
        urls = read_urls_from_file(str(urls_file))
        
        for url in urls:
            if output_path := capture_screenshot(url, output_dir, options):
                logger.info(f"Screenshot saved for {url} to: {output_path}")
            else:
                logger.error(f"Failed to capture screenshot for: {url}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()