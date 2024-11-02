import os
import logging
import datetime
from typing import Dict, List
from dotenv import load_dotenv
from apify_client import ApifyClient
import csv
from pathlib import Path
import urllib.request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApifyYoutubeScreenshot:
    """Handle YouTube screenshots using Apify."""
    
    def __init__(self):
        """Initialize with API token from .env"""
        load_dotenv()
        self.token = os.getenv('APIFY_API_TOKEN')
        if not self.token:
            raise ValueError("APIFY_API_TOKEN not found in .env")
        
        self.client = ApifyClient(self.token)
        self.default_input = {
            "delay": 1000,
            "delayAfterScrolling": 2500,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
                "apifyProxyCountry": "US"
            },
            "scrollToBottom": True,
            "viewportWidth": 1280,
            "format": "png",
            "waitUntil": "networkidle2",
            "waitUntilNetworkIdleAfterScroll": False,
            "waitUntilNetworkIdleAfterScrollTimeout": 30000
        }

    def save_screenshot(self, screenshot_url: str, output_path: str) -> None:
        """Save screenshot from URL to file."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(screenshot_url, output_path)
            logger.info(f"Saved screenshot to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            raise

    def take_screenshots(self, urls: List[str], output_folder: Path) -> None:
        """
        Take screenshots using Apify service and save them.
        
        Args:
            urls: List of YouTube URLs to capture
            output_folder: Path to save screenshots
        """
        formatted_urls = [{"url": url, "method": "GET"} for url in urls]
        run_input = {
            **self.default_input,
            "urls": formatted_urls
        }

        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor("rGCyoaKTKhyMiiTvS").call(run_input=run_input)
            
            # Save screenshots from results
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                if screenshot_url := item.get('screenshotUrl'):
                    # Extract channel name from URL
                    url = item['url']
                    channel_name = url.split('@')[-1].split('/')[0]
                    
                    # Determine output path
                    screenshot_path = output_folder / channel_name / 'apify_screenshot.png'
                    self.save_screenshot(screenshot_url, str(screenshot_path))
            
        except Exception as e:
            logger.error(f"Error taking screenshots: {e}")
            raise

    def process_csv(self, csv_path: str) -> None:
        """Process YouTube URLs from CSV and take screenshots."""
        try:
            # Setup output folder
            data_folder = Path(os.path.dirname(os.path.dirname(__file__))) / 'data'
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_folder = data_folder / f'apify_snapshots_{timestamp}'

            # Read URLs from CSV
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                urls = [row['youtube_url'] for row in reader if row.get('youtube_url')]
                
            # Take and save screenshots
            self.take_screenshots(urls, output_folder)
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            raise

def main():
    """Main entry point."""
    try:
        screenshot = ApifyYoutubeScreenshot()
        data_folder = Path(__file__).parent.parent / 'data'
        screenshot.process_csv(str(data_folder / 'youtuber.csv'))
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()