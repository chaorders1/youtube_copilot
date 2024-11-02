"""
This module provides functionality to split large images into smaller parts.

The main functionality includes splitting images into multiple parts based on a specified
height while maintaining the original width. It handles various image formats and creates
appropriately named output files.

Key features:
- Splits images into parts of specified height
- Maintains original image width and quality
- Supports common image formats (JPEG, PNG, GIF, etc.)
- Creates output directory if needed
- Handles large images efficiently
- Includes error handling for file operations

Usage:
    python split_picture.py --input_file "/path/to/your/image.jpg" --output_dir "/path/to/output"
    
    # Or from another Python file:
    from utility.split_picture import split_picture
    split_picture('/path/to/image.jpg', '/path/to/output', part_height=1024)
"""

from PIL import Image
import os
import argparse

def get_output_format(input_file):
    # Get the file extension (format) of the input file
    _, ext = os.path.splitext(input_file)
    ext = ext.lower()

    # Map of common image extensions to PIL format strings
    format_map = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.gif': 'GIF',
        '.bmp': 'BMP',
        '.tiff': 'TIFF'
    }

    # Return the format, defaulting to JPEG if unknown
    return format_map.get(ext, 'JPEG')

def split_picture(input_file, output_dir, part_height=1024):
    """
    Split an image into multiple parts vertically.
    
    Args:
        input_file (str): Full path to the input image file
        output_dir (str): Full path to the output directory
        part_height (int, optional): Height of each part in pixels. Defaults to 1024.
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid image
    """
    # Validate input file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    try:
        # Open the input image
        with Image.open(input_file) as img:
            # Get the dimensions of the image
            width, height = img.size
            
            # Calculate the number of parts
            num_parts = (height + part_height - 1) // part_height
            
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the output format
            output_format = get_output_format(input_file)
            
            # Get the appropriate file extension for the output format
            extension = '.jpg' if output_format == 'JPEG' else f'.{output_format.lower()}'
            
            # Get base filename without extension
            base_filename = os.path.splitext(os.path.basename(input_file))[0]
            
            # Split the image into parts
            for i in range(num_parts):
                top = i * part_height
                bottom = min((i + 1) * part_height, height)
                
                # Crop the image
                part = img.crop((0, top, width, bottom))
                
                # Save the part using the original filename as prefix
                output_file = os.path.join(output_dir, f"{base_filename}_part_{i+1}{extension}")
                part.save(output_file, output_format)
                print(f"Saved {output_file}")
                
    except (IOError, OSError) as e:
        raise ValueError(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split an image into multiple parts vertically.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python split_picture.py --input_file "C:/Users/Photos/image.jpg" --output_dir "C:/Users/Photos/split_output"
    python split_picture.py --input_file "/home/user/image.png" --output_dir "/home/user/split" --part_height 800
        """
    )
    parser.add_argument("--input_file", required=True, help="Full path to the input image file")
    parser.add_argument("--output_dir", required=True, help="Full path to output directory")
    parser.add_argument("--part_height", type=int, default=1024, help="Height of each part in pixels (default: 1024)")
    
    args = parser.parse_args()

    try:
        split_picture(args.input_file, args.output_dir, args.part_height)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {str(e)}")
        exit(1)