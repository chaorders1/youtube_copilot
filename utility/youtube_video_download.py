"""
YouTube Video Downloader Utility
===============================

A simple utility to download YouTube videos using yt-dlp library.
Videos are downloaded in MP4 format to the '../data/youtube_video' directory.

Prerequisites:
-------------
- Python 3.6+
- yt-dlp library (install using: pip install yt-dlp)

Usage Examples:
-------------
1. Basic usage with video URL:
    python youtube_video_download.py url='https://www.youtube.com/watch?v=example'

2. Usage with @ symbol (both work the same):
    python youtube_video_download.py url='@https://www.youtube.com/watch?v=example'

3. Usage with different video formats:
    - Full video URLs: 
        python youtube_video_download.py url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    - Short URLs: 
        python youtube_video_download.py url='https://youtu.be/dQw4w9WgXcQ'

Output:
-------
- Videos are saved to '../data/youtube_video' directory
- Filename format: '{video_title}.mp4'
- Progress and status are logged to console

Note:
-----
- Make sure to run this script from the utility directory
- URLs must be enclosed in quotes
- The download directory is created automatically if it doesn't exist
"""

import os
import sys
from pathlib import Path
import logging
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """A class to handle YouTube video downloads using yt-dlp."""

    def __init__(self, output_path: str = '../data/youtube_video'):
        """Initialize the YouTube downloader."""
        self.output_path = output_path
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        self.ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }

    def download_video(self, url: str) -> bool:
        """Download a YouTube video from the given URL."""
        if not url:
            logger.error('URL cannot be empty')
            return False

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                logger.info(f'Downloading video: {url}')
                ydl.download([url])
                logger.info('Download completed successfully')
                return True

        except Exception as e:
            logger.error(f'Download failed: {str(e)}')
            return False

def parse_args(args):
    """Parse command line arguments in the format key='value'."""
    params = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            # Remove any quotes around the value
            value = value.strip('\'"')
            params[key] = value
    return params

def main():
    """Handle command line execution."""
    args = parse_args(sys.argv[1:])
    
    if 'url' not in args:
        print("Usage: python youtube_video_download.py url='YOUR_YOUTUBE_URL'")
        return

    downloader = YouTubeDownloader()
    url = args['url'].strip('@')  # Remove @ if present
    
    if downloader.download_video(url):
        print('Video downloaded successfully!')
    else:
        print('Failed to download video.')

if __name__ == '__main__':
    main()

