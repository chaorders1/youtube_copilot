"""
Screenshot Utility

This module provides functionality to capture website screenshots using the ScreenshotAPI service.
It specializes in capturing YouTube channel pages with optimized settings.

Example Usage:
    # Basic usage - capture YouTube channel
    screenshot = ScreenshotAPI(api_token)
    screenshot.capture('https://www.youtube.com/@veritasium', 'output.png')
    
    # Command line usage:
    # Single channel capture:
    python screenshotapi_url.py --url='https://www.youtube.com/@veritasium'
    python screenshotapi_url.py --url='https://www.youtube.com/@TuCOSMOPOLIS'
"""

#!/usr/bin/python3
import urllib.parse
import urllib.request
import os
import argparse
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScreenshotAPI:
    """Handles screenshot capture using ScreenshotAPI service."""
    
    BASE_URL = "https://shot.screenshotapi.net/screenshot"
    
    DEFAULT_OPTIONS = {
        # Output settings
        'output': 'image',
        'file_type': 'png',
        'width': '1920',
        'height': '3240',
        'full_page': 'false',
        
        # Loading optimizations 
        'delay': '12000',
        'wait_for_event': 'networkidle0',# Wait for all network requests to finish
        'lazy_load': 'true',  # Enable lazy loading detection
        'fresh': 'true',  # Always get fresh screenshot
        
        # Content blocking
        'block_ads': 'true',
        'no_cookie_banners': 'true',
        
        # Quality settings
        'retina': 'false'    
    }
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        # Allow unverified SSL for the API
        ssl._create_default_https_context = ssl._create_unverified_context
        
    def capture(self, url: str, output_path: str, custom_options: Optional[Dict] = None) -> bool:
        """Capture screenshot of URL and save to output path."""
        try:
            # Prepare parameters
            params = self.DEFAULT_OPTIONS.copy()
            if custom_options:
                params.update(custom_options)
            params['token'] = self.api_token
            params['url'] = url
            
            # Construct query URL
            query = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Capture screenshot
            urllib.request.urlretrieve(query, output_path)
            logger.info(f"Screenshot saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            return False

def main():
    """Main function to handle command line arguments."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Capture website screenshots using ScreenshotAPI')
    parser.add_argument('--url', required=True, help='URL to capture')
    args = parser.parse_args() 
    
    api_token = os.getenv('SCREENSHOT_API_TOKEN')
    if not api_token:
        logger.error("SCREENSHOT_API_TOKEN not found in environment variables")
        return
        
    api = ScreenshotAPI(api_token)
    output_path = os.path.join('screenshots', 'screenshot.png')
    api.capture(args.url, output_path)

if __name__ == "__main__":
    main()