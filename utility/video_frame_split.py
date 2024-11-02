import cv2
import os
from pathlib import Path

def video_frame_split(video_path: str, output_dir: str = None, time_interval: float = None) -> None:
    """
    Extract frames from a video file and save them as images.
    
    Args:
        video_path: Path to the input video file
        output_dir: Directory to save extracted frames (if None, will create based on video name)
        time_interval: Extract frames every n seconds
    """
    # Get video filename and create output directory name
    video_path = Path(video_path)
    video_name = video_path.stem  # Gets filename without extension
    
    # If output_dir is not specified, create one based on video name
    if not output_dir:
        output_dir = f'frames_{video_name}'
    
    # Get absolute path to the project root (parent of utility folder)
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / 'data' / output_dir
    
    # Create the output directory if it doesn't exist
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
    
    # If time_interval is set, calculate the frame_interval
    if time_interval is not None:
        frame_interval = int(fps * time_interval)
    else:
        frame_interval = 1
    
    print(f'Video properties:')
    print(f'- Total frames: {frame_count}')
    print(f'- FPS: {fps}')
    print(f'- Frame interval: {frame_interval} frames')
    
    frame_number = 0
    saved_count = 0
    
    while True:
        success, frame = video.read()
        
        if not success:
            break
            
        if frame_number % frame_interval == 0:
            frame_path = output_path / f'frame_{saved_count:06d}.jpg'
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

