"""
Simple Screenshot Batch Processing Tool

# Specify custom output directory
python screenshotapi_batch.py --input /Users/yuanlu/Desktop/youtube_channel_10.csv --columns youtube_channel_url,youtube_channel_videos_url --output /Users/yuanlu/Desktop/snapshot_test

# Default output directory will be 'screenshots' if not specified
python screenshotapi_batch.py --input urls.csv --columns url

Required Environment Variable:
    SCREENSHOT_API_TOKEN: Your API authentication token
"""

import os
import time
import logging
import argparse
import pandas as pd
from typing import List
from screenshotapi_url import ScreenshotAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def take_screenshots(urls: List[str], api_token: str, output_dir: str, delay: float = 1.0) -> int:
    """
    Take screenshots of URLs sequentially.
    Returns the number of successful captures.
    """
    api = ScreenshotAPI(api_token, output_dir=output_dir)
    success_count = 0

    for url in urls:
        try:
            if filepath := api.capture(url):
                logger.info(f"✓ {url} -> {filepath}")
                success_count += 1
            else:
                logger.error(f"✗ Failed: {url}")
        except Exception as e:
            logger.error(f"✗ Error with {url}: {str(e)}")
        
        time.sleep(delay)  # Respect API rate limits
    
    return success_count

def main():
    parser = argparse.ArgumentParser(description="Batch screenshot capture from CSV")
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--columns', required=True, help='Column names with URLs (comma-separated)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--output', default='screenshots', help='Output directory for screenshots')
    args = parser.parse_args()

    try:
        # Read and prepare URLs
        df = pd.read_csv(args.input)
        columns = [col.strip() for col in args.columns.split(',')]
        
        if missing := set(columns) - set(df.columns):
            raise ValueError(f"Columns not found: {', '.join(missing)}")
        
        urls = []
        for col in columns:
            urls.extend(df[col].dropna().tolist())
        
        # Clean URLs
        urls = list(set(url.strip() for url in urls if url.strip()))
        logger.info(f"Found {len(urls)} unique URLs")

        # Get API token
        if not (api_token := os.getenv('SCREENSHOT_API_TOKEN')):
            raise ValueError("SCREENSHOT_API_TOKEN not set")

        # Process URLs with output directory
        success_count = take_screenshots(urls, api_token, args.output, args.delay)
        
        # Report results
        logger.info(f"Completed: {success_count}/{len(urls)} screenshots captured")
        return 0 if success_count else 1

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())