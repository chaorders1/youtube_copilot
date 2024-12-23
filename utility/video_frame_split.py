"""Video Frame Extraction Utility

This module provides functionality to extract frames from video files at specified intervals.
It saves the frames as JPEG images and generates detailed metadata about the extraction process.

Example Usage:
    # Basic usage - extract every frame
    video_frame_split('path/to/video.mp4')
    
    # Extract frames every 10 seconds with custom output directory
    video_frame_split('path/to/video.mp4', output_dir='my_frames', time_interval=10.0)
    
    # Command line usage:
    # python video_frame_split.py "/Users/yuanlu/Code/youtube_copilot/data/youtube_video/video.mp4"
    # python video_frame_split.py "/Users/yuanlu/Code/youtube_copilot/data/video_two_gpt-4os_interacting_and_singing/Two_GPT-4os_interacting_and_singing.mp4" frames_output 5.0
    # python video_frame_split.py "/Users/yuanlu/Code/youtube_copilot/data/video_claude_computer_use_for_coding/Claude_Computer_use_for_coding.mp4" frames_output 5.0

Features:
    - Extracts frames at specified time intervals
    - Generates comprehensive metadata file
    - Supports various video formats (MP4, AVI, MOV, etc.)
    - Progress tracking during extraction
    - Organized output directory structure
    - Detailed timestamp and frame information in filenames

Output Structure:
    output_dir/
    ├── metadata.txt                      # Extraction metadata and video information
    └── frames/
        ├── timestamp_000000_frame_0000_time_0.0s.jpg
        ├── timestamp_000010_frame_0300_time_10.0s.jpg
        └── ...

Requirements:
    - OpenCV (cv2)
    - Python 3.6+

Notes:
    - Frame filenames include timestamp and frame number for easy reference
    - Metadata includes video properties, extraction settings, and processing details
    - Output directory is created automatically if it doesn't exist
"""

import cv2
import os
from pathlib import Path
from datetime import datetime

def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def video_frame_split(video_path: str, output_dir: str = None, time_interval: float = None) -> None:
    """
    Extract frames from a video file and save them as images.
    
    Args:
        video_path: Path to the input video file
        output_dir: Directory to save extracted frames (if None, will create based on video name)
        time_interval: Extract frames every n seconds
    """
    # Step 1: Get video filename
    video_path = Path(video_path)
    video_name = video_path.stem  # Gets filename without extension
    
    # Step 2: Determine output directory name
    if output_dir:
        # If custom output_dir provided, check if it starts with 'frames_'
        prefix = '' if output_dir.startswith('frames_') else 'frames_'
        output_dir = f'{prefix}{output_dir}_{video_name}'
    else:
        # If no output_dir provided, just use video name
        output_dir = f'frames_{video_name}'
    
    # Step 3: Setup output path
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / 'data' / output_dir
    
    # Step 4: Create the output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f'Project root: {project_root}')
    print(f'Opening video file: {video_path}')
    print(f'Frames will be saved to: {output_path}')
    
    # Open video file
    video = cv2.VideoCapture(str(video_path))
    
    if not video.isOpened():
        raise ValueError(f'Error opening video file: {video_path}')
    
    # Get video properties
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    duration = frame_count / fps  # Total duration in seconds
    
    # Calculate frame interval based on time_interval
    frame_interval = int(time_interval * fps) if time_interval else 1
    
    # Get additional video properties
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = int(video.get(cv2.CAP_PROP_FOURCC))
    codec_name = ''.join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
    
    # Create metadata file with enhanced information
    metadata_path = output_path / 'metadata.txt'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(f"Video Metadata:\n")
        f.write(f"==============\n\n")
        f.write(f"Source Information:\n")
        f.write(f"- Video File: {video_name}\n")
        f.write(f"- Original Path: {video_path}\n")
        f.write(f"- Codec: {codec_name}\n")
        
        f.write(f"\nVideo Properties:\n")
        f.write(f"- Resolution: {width}x{height}\n")
        f.write(f"- FPS: {fps}\n")
        f.write(f"- Total Frames: {frame_count}\n")
        f.write(f"- Duration: {format_timestamp(duration)} ({duration:.2f} seconds)\n")
        
        f.write(f"\nExtraction Settings:\n")
        f.write(f"- Frame Interval: {time_interval if time_interval else '1/fps'} seconds\n")
        f.write(f"- Frames Saved Every: {frame_interval} frames\n")
        f.write(f"- Output Directory: {output_path}\n")
        
        f.write(f"\nFile Naming Convention:\n")
        f.write(f"timestamp_HHMMSS_frame_XXXX_time_YYYYs.jpg\n")
        f.write(f"where:\n")
        f.write(f"- HHMMSS: Timestamp in hours:minutes:seconds\n")
        f.write(f"- XXXX: Frame number (zero-padded)\n")
        f.write(f"- YYYY: Timestamp in seconds\n")
        
        f.write(f"\nProcessing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    frame_number = 0
    saved_count = 0
    
    while True:
        success, frame = video.read()
        
        if not success:
            break
            
        if frame_number % frame_interval == 0:
            # Calculate timestamp
            timestamp_seconds = frame_number / fps
            timestamp_hhmmss = format_timestamp(timestamp_seconds)
            
            # Create frame filename with metadata
            frame_filename = (
                f"timestamp_{timestamp_hhmmss.replace(':', '')}_"
                f"frame_{frame_number:04d}_"
                f"time_{timestamp_seconds:.1f}s.jpg"
            )
            
            frame_path = output_path / frame_filename
            cv2.imwrite(str(frame_path), frame)
            saved_count += 1
            
        frame_number += 1
        
        # Print progress every 100 frames
        if frame_number % 100 == 0:
            print(f'Processed {frame_number} frames, saved {saved_count} frames')
    
    video.release()
    print(f'\nCompleted:')
    print(f'- Total frames processed: {frame_number}')
    print(f'- Frames saved: {saved_count}')
    print(f'- Output location: {output_path}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video_frame_split.py <video_path> [output_dir] [time_interval_seconds]")
        sys.exit(1)
        
    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    time_interval = float(sys.argv[3]) if len(sys.argv) > 3 else None
    
    try:
        video_frame_split(video_path, output_dir, time_interval=time_interval)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

