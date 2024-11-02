"""Image Cropping Utility

This module provides functionality to crop large images into smaller parts vertically.
It maintains the original image quality and width while dividing it into specified heights.

Example Usage:
    # Basic usage with default height (800px) and overlap (200px)
    python picture_crop.py "/Users/yuanlu/Code/youtube_copilot/data/snapshot/anthropic_youtube_chanel.png"
    
    # With custom output directory
    python picture_crop.py "/Users/yuanlu/Code/youtube_copilot/data/snapshot/anthropic_youtube_chanel.png" custom_output
    
    # With custom height (1024px)
    python picture_crop.py "/Users/yuanlu/Code/youtube_copilot/data/snapshot/anthropic_youtube_chanel.png" custom_output 1024
    
    # Full options (image, output dir, height, overlap)
    python picture_crop.py "/Users/yuanlu/Code/youtube_copilot/data/snapshot/anthropic_youtube_chanel.png" custom_output 1024 100

Features:
    - Crops images into parts of specified height
    - Maintains original image width and quality
    - Supports multiple image formats (JPEG, PNG, GIF, BMP, TIFF)
    - Configurable overlap between parts
    - Organized output directory structure
    - Detailed metadata generation

Output Structure:
    output_dir/
    ├── metadata.txt           # Crop information and image properties
    └── parts/
        ├── original_name_part_1_h800_overlap200.jpg
        ├── original_name_part_2_h800_overlap200.jpg
        └── ...

Requirements:
    - PIL (Python Imaging Library)
    - Python 3.6+
"""

from PIL import Image
import os
from pathlib import Path
from datetime import datetime

def get_output_format(input_file: str) -> str:
    """Get the appropriate output format based on input file extension."""
    ext = Path(input_file).suffix.lower()
    
    format_map = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.gif': 'GIF',
        '.bmp': 'BMP',
        '.tiff': 'TIFF'
    }
    
    return format_map.get(ext, 'JPEG')

def crop_picture(input_file: str, output_dir: str = None, part_height: int = 800, overlap: int = 200) -> None:
    """
    Crop an image into multiple parts vertically with overlap.
    
    Args:
        input_file: Path to the input image
        output_dir: Directory to save cropped parts (if None, will create based on image name)
        part_height: Height of each part in pixels (default: 800)
        overlap: Height of overlap between parts in pixels (default: 200)
    """
    # Step 1: Setup paths
    input_path = Path(input_file)
    image_name = input_path.stem
    
    # Step 2: Determine output directory
    if output_dir:
        # If custom output_dir provided, check if it starts with 'crop_'
        prefix = '' if output_dir.startswith('crop_') else 'crop_'
        output_dir = f'{prefix}{output_dir}_{image_name}'
    else:
        output_dir = f'crop_{image_name}'
    
    # Step 3: Setup output path
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / 'data' / output_dir
    
    # Step 4: Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f'Project root: {project_root}')
    print(f'Processing image: {input_path}')
    print(f'Parts will be saved to: {output_path}')
    
    # Open and process the image
    with Image.open(input_path) as img:
        width, height = img.size
        num_parts = (height + part_height - 1) // part_height
        
        # Get output format
        output_format = get_output_format(str(input_path))
        extension = '.jpg' if output_format == 'JPEG' else f'.{output_format.lower()}'
        
        # Create metadata file
        metadata_path = output_path / 'metadata.txt'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Image Crop Metadata:\n")
            f.write(f"==================\n\n")
            f.write(f"Source Information:\n")
            f.write(f"- Image File: {image_name}\n")
            f.write(f"- Original Path: {input_path}\n")
            f.write(f"- Format: {output_format}\n")
            
            f.write(f"\nImage Properties:\n")
            f.write(f"- Dimensions: {width}x{height}\n")
            f.write(f"- Mode: {img.mode}\n")
            
            f.write(f"\nCrop Settings:\n")
            f.write(f"- Part Height: {part_height} pixels\n")
            f.write(f"- Overlap: {overlap} pixels\n")
            f.write(f"- Number of Parts: {num_parts}\n")
            f.write(f"- Output Directory: {output_path}\n")
            
            f.write(f"\nFile Naming Convention:\n")
            f.write(f"original_name_part_X_h{part_height}_overlap{overlap}{extension}\n")
            f.write(f"where:\n")
            f.write(f"- original_name: Name of the source image\n")
            f.write(f"- X: Part number\n")
            f.write(f"- h{part_height}: Height of each part\n")
            f.write(f"- overlap{overlap}: Overlap between parts\n")
            
            f.write(f"\nProcessing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Crop and save parts with overlap
        for i in range(num_parts):
            # Calculate crop boundaries with overlap
            top = max(0, i * (part_height - overlap))
            bottom = min(height, top + part_height)
            
            part = img.crop((0, top, width, bottom))
            output_file = output_path / f"{image_name}_part_{i+1}_h{part_height}_overlap{overlap}{extension}"
            part.save(output_file, output_format)
            print(f"Saved part {i+1}/{num_parts}: {output_file}")
            print(f"  Position: {top} to {bottom} pixels")
        
        print(f'\nCompleted:')
        print(f'- Parts created: {num_parts}')
        print(f'- Output location: {output_path}')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python picture_crop.py <image_path> [output_dir] [part_height] [overlap]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    part_height = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    overlap = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    
    try:
        crop_picture(image_path, output_dir, part_height, overlap)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)