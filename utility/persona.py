"""
Module for analyzing YouTube channel personas using Claude API.
"""
import os
import base64
import argparse
from pathlib import Path
from typing import List, Dict
import logging
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PersonaAnalyzer:
    """
    A class to analyze YouTube channel personas using Claude API.
    """
    def __init__(self, api_key: str = None):
        """
        Initialize the PersonaAnalyzer.

        Args:
            api_key (str, optional): Anthropic API key. Defaults to environment variable.
        """
        self.client = Anthropic(api_key=api_key)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """
        Load the prompt template from the markdown file.

        Returns:
            str: The prompt template content
        """
        prompt_path = Path(__file__).parent.parent / 'prompt' / 'prompt_persona.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found at {prompt_path}")
            raise

    def _encode_image(self, image_path: Path) -> Dict:
        """
        Encode an image file to base64.

        Args:
            image_path (Path): Path to the image file

        Returns:
            Dict: Message content dict with image data
        """
        try:
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                return {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': f'image/{image_path.suffix[1:]}',
                        'data': base64_image
                    }
                }
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {str(e)}")
            raise

    def analyze_channel(self, images_folder: str | Path) -> str:
        """
        Analyze YouTube channel using images from specified folder.

        Args:
            images_folder (str | Path): Path to folder containing channel screenshots

        Returns:
            str: Analysis results from Claude
        """
        images_path = Path(images_folder).resolve()  # Get absolute path
        logger.info(f"Analyzing channel from folder: {images_path}")
        
        if not images_path.exists():
            raise FileNotFoundError(f"Images folder not found: {images_path}")

        # Get all image files
        image_files = [
            f for f in images_path.iterdir() 
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png')
        ]

        if not image_files:
            raise ValueError(f"No image files found in {images_path}")

        logger.info(f"Found {len(image_files)} images to analyze")

        # Prepare message content
        message_content = []
        
        # Add all images
        for image_file in image_files:
            message_content.append(self._encode_image(image_file))

        # Add the prompt text
        message_content.append({
            'type': 'text',
            'text': self.prompt_template
        })

        try:
            # Create message using Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022", # don't change this model
                max_tokens=1000, # don't change this max_tokens
                temperature=0,
                messages=[{
                    'role': 'user',
                    'content': message_content
                }]
            )
            # Extract text content from response
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze YouTube channel content from screenshots.'
    )
    parser.add_argument(
        'images_folder',
        type=str,
        help='Path to folder containing channel screenshots'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to save analysis results (default: <images_folder>_analysis.md)',
        default=None
    )
    return parser.parse_args()

def main():
    """Main function to demonstrate usage."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize analyzer (API key from environment variable)
        analyzer = PersonaAnalyzer()
        
        # Analyze channel from specified folder
        result = analyzer.analyze_channel(args.images_folder)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Create output next to input folder with timestamp
            input_path = Path(args.images_folder)
            output_path = input_path.parent / f"{input_path.name}_analysis.md"
        
        # Save results to markdown file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding='utf-8')
        logger.info(f'Analysis results saved to {output_path}')
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main()