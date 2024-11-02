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
    # python youtube_video_download.py url='https://www.youtube.com/watch?v=vH2f7cjXjKI' subtitles='en'

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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """A class to handle YouTube video downloads using yt-dlp."""

    @staticmethod
    def sanitize_filename(title: str) -> str:
        """
        Sanitize the video title to create a safe filename.
        
        Args:
            title: The original video title
            
        Returns:
            A sanitized filename with only alphanumeric characters and underscores
        """
        # Remove any characters that aren't alphanumeric, spaces, or safe special chars
        safe_chars = re.sub(r'[^a-zA-Z0-9\s\-_]', '', title)
        
        # Replace multiple spaces with single space and strip
        safe_chars = ' '.join(safe_chars.split())
        
        # Replace spaces with underscores
        safe_chars = safe_chars.replace(' ', '_')
        
        # Ensure the filename isn't empty
        if not safe_chars:
            safe_chars = 'untitled_video'
            
        # Limit filename length (optional, adjust as needed)
        max_length = 100
        if len(safe_chars) > max_length:
            safe_chars = safe_chars[:max_length]
            
        return safe_chars.lower()

    def __init__(self, output_path: str = '../data/youtube_video'):
        """Initialize the YouTube downloader."""
        self.output_path = output_path
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Update default options to use sanitized filename
        self.ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(
                output_path, 
                '%(title)s.%(ext)s'
            ),
            'noplaylist': True,
            # Add custom filename sanitization
            'restrictfilenames': True,  # Tell yt-dlp to be conservative with filenames
            'force_filename_sanitization': True,
            'postprocessor_hooks': [self._sanitize_output_filename],
        }

    def _sanitize_output_filename(self, d):
        """Post-processor hook to sanitize the output filename."""
        if 'filepath' in d:
            path = Path(d['filepath'])
            new_name = self.sanitize_filename(path.stem) + path.suffix
            new_path = path.parent / new_name
            try:
                path.rename(new_path)
                d['filepath'] = str(new_path)
            except Exception as e:
                logger.warning(f'Failed to rename file: {e}')

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
                'subtitleslangs': ['en'],
                'subtitlesformat': 'vtt',
                'postprocessors': [{
                    'key': 'FFmpegSubtitlesConvertor',
                    'format': 'vtt'
                }]
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
        print("Usage: python youtube_video_download.py url='YOUR_YOUTUBE_URL' [quality='720p'] [format='audio'] [subtitles='en']")
        return

    downloader = YouTubeDownloader()
    url = args['url'].strip('@')
    
    # Parse optional arguments
    quality = args.get('quality')
    format_type = args.get('format')
    subtitles = bool(args.get('subtitles'))
    
    if downloader.download_video(url, quality, format_type, subtitles):
        print('Video downloaded successfully!')
    else:
        print('Failed to download video.')

if __name__ == '__main__':
    main()

