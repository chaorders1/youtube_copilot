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
1. Download video in default format (MP4):
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ'

2. Download with specific quality:
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' quality='best'
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' quality='720p'
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' quality='worst'

3. Download audio only:
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' format='audio'

4. Download with subtitles:
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' subtitles='true'

5. Download specific format:
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' format='mp4'
    python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' format='webm'

Available Options:
----------------
- quality: 'best', '4k', '1080p', '720p', '480p', '360p', 'worst'
- format: 'video' (default), 'audio', 'mp4', 'webm'
- subtitles: 'true' or 'false'
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
        
        # Default options
        self.ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }

    def _get_format_options(self, quality=None, format_type=None, subtitles=False):
        """Configure download options based on user preferences."""
        if format_type == 'audio':
            self.ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            })
        elif quality:
            if quality == 'best':
                self.ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif quality == 'worst':
                self.ydl_opts['format'] = 'worstvideo+worstaudio/worst'
            else:
                # For specific resolutions like 720p, 1080p, etc.
                self.ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best'

        if subtitles:
            self.ydl_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitlesformat': 'srt',
            })

    def download_video(self, url: str, quality=None, format_type=None, subtitles=False) -> bool:
        """Download a YouTube video with specified options."""
        if not url:
            logger.error('URL cannot be empty')
            return False

        try:
            self._get_format_options(quality, format_type, subtitles)
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                logger.info(f'Downloading video: {url}')
                logger.info(f'Using options: {self.ydl_opts}')
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
        print("Usage: python youtube_video_download.py url='YOUR_YOUTUBE_URL' [quality='720p'] [format='audio'] [subtitles='true']")
        return

    downloader = YouTubeDownloader()
    url = args['url'].strip('@')
    
    # Parse optional arguments
    quality = args.get('quality')
    format_type = args.get('format')
    subtitles = args.get('subtitles', '').lower() == 'true'
    
    if downloader.download_video(url, quality, format_type, subtitles):
        print('Video downloaded successfully!')
    else:
        print('Failed to download video.')

if __name__ == '__main__':
    main()

