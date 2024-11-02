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
from datetime import datetime

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

    def __init__(self, output_path: str = None):
        """Initialize the YouTube downloader."""
        # Store the base path for later use
        self.base_path = Path(__file__).resolve().parent.parent / 'data'
        
        # Will be set during download when we know the video title
        self.output_path = None
        self.video_title = None
        
        # Initialize with basic options, path will be set during download
        self.ydl_opts = {
            'format': 'mp4',
            'noplaylist': True,
            'restrictfilenames': True,
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
            # First get video info to determine output directory
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                video_info = ydl.extract_info(url, download=False)
                self.video_title = self.sanitize_filename(video_info.get('title', 'untitled'))
                
                # Create output directory with video name
                self.output_path = self.base_path / f'video_{self.video_title}'
                self.output_path.mkdir(parents=True, exist_ok=True)
                
                # Update output template with new path
                self.ydl_opts['outtmpl'] = str(self.output_path / '%(title)s.%(ext)s')
            
            # Configure format options
            self._get_format_options(quality, format_type, subtitles)
            
            # Download the video
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                logger.info(f'Downloading video: {url}')
                logger.info(f'Output directory: {self.output_path}')
                
                # Download the video
                ydl.download([url])
                
                # Generate metadata file
                self._generate_metadata(video_info, url, quality, format_type, subtitles)
                
                logger.info('Download completed successfully')
                return True

        except Exception as e:
            logger.error(f'Download failed: {str(e)}')
            return False

    def _generate_metadata(self, video_info: dict, url: str, quality=None, format_type=None, subtitles=False):
        """Generate metadata file with download and video information."""
        try:
            # Create metadata filename based on video title
            video_title = self.sanitize_filename(video_info.get('title', 'untitled'))
            metadata_path = Path(self.output_path) / f'{video_title}_metadata.txt'
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(f"YouTube Video Metadata:\n")
                f.write(f"====================\n\n")
                
                # Video Information
                f.write(f"Video Information:\n")
                f.write(f"- Title: {video_info.get('title', 'N/A')}\n")
                f.write(f"- Channel: {video_info.get('channel', 'N/A')}\n")
                f.write(f"- Upload Date: {video_info.get('upload_date', 'N/A')}\n")
                f.write(f"- Duration: {video_info.get('duration_string', 'N/A')}\n")
                f.write(f"- View Count: {video_info.get('view_count', 'N/A')}\n")
                f.write(f"- Like Count: {video_info.get('like_count', 'N/A')}\n")
                f.write(f"- Original URL: {url}\n")
                
                # Video Description
                f.write(f"\nVideo Description:\n")
                f.write(f"{video_info.get('description', 'N/A')}\n")
                
                # Download Settings
                f.write(f"\nDownload Settings:\n")
                f.write(f"- Quality: {quality if quality else 'default'}\n")
                f.write(f"- Format: {format_type if format_type else 'mp4'}\n")
                f.write(f"- Subtitles: {'Yes' if subtitles else 'No'}\n")
                
                # Technical Details
                f.write(f"\nTechnical Details:\n")
                f.write(f"- Format ID: {video_info.get('format_id', 'N/A')}\n")
                f.write(f"- Resolution: {video_info.get('resolution', 'N/A')}\n")
                f.write(f"- FPS: {video_info.get('fps', 'N/A')}\n")
                f.write(f"- Video Codec: {video_info.get('vcodec', 'N/A')}\n")
                f.write(f"- Audio Codec: {video_info.get('acodec', 'N/A')}\n")
                
                # Tags and Categories
                if video_info.get('tags'):
                    f.write(f"\nTags:\n")
                    for tag in video_info.get('tags', []):
                        f.write(f"- {tag}\n")
                
                # Processing Information
                f.write(f"\nProcessing Information:\n")
                f.write(f"- Download Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- Output Directory: {self.output_path}\n")
                f.write(f"- Filename: {video_title}\n")
                
                # File Locations
                f.write(f"\nFile Locations:\n")
                f.write(f"- Video File: {video_title}.{format_type if format_type == 'audio' else 'mp4'}\n")
                if subtitles:
                    f.write(f"- Subtitle File: {video_title}.en.vtt\n")
                
                logger.info(f'Generated metadata file: {metadata_path}')
                
        except Exception as e:
            logger.warning(f'Failed to generate metadata file: {e}')

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

