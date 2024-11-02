"""YouTube Video Downloader Utility

This module provides functionality to download YouTube videos using yt-dlp library.
It saves videos and optional subtitles to a specified output directory.

Example Usage:
    # Basic usage - download video in default MP4 format
    video_download('https://www.youtube.com/watch?v=ODaHJzOyVCQ')
    
    # Download with specific quality and custom output
    video_download('https://www.youtube.com/watch?v=ODaHJzOyVCQ', 
                  quality='720p',
                  output_dir='my_videos')
    
    # Command line usage:
    # Download video in MP4 format:
    # python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ'
    
    # Download audio only:
    # python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' format='audio'
    
    # Download with English subtitles:
    # python youtube_video_download.py url='https://www.youtube.com/watch?v=ODaHJzOyVCQ' subtitles='en'

Features:
    - Downloads videos in various formats (MP4, WebM, audio-only)
    - Supports multiple quality options (4K, 1080p, 720p, etc.)
    - Optional subtitle download in multiple languages
    - Progress tracking during download
    - Organized output directory structure
    - Detailed logging of download process

Output Structure:
    data/youtube_video/
    ├── video_title.mp4           # Downloaded video file
    ├── video_title.en.vtt        # English subtitles (if requested)
    ├── video_title.es.vtt        # Spanish subtitles (if requested)
    └── video_title.mp3           # Audio-only file (if audio format selected)

Requirements:
    - Python 3.6+
    - yt-dlp library (pip install yt-dlp)

Notes:
    - Videos are saved to 'data/youtube_video' by default
    - Supports both video and audio-only downloads
    - Quality options: 'best', '4k', '1080p', '720p', '480p', '360p', 'worst'
    - Format options: 'video', 'audio', 'mp4', 'webm'
    - Subtitle options: 'en', 'es', 'fr', 'de', etc. (ISO 639-1 codes)
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

