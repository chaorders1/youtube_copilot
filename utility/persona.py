"""
Module for analyzing YouTube channel personas using Claude API.
"""
import os
import base64
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from anthropic import Anthropic
import PyPDF2
import docx
import csv
import json
import html2text
import ebooklib
from ebooklib import epub

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
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png'}
    SUPPORTED_TEXT_FORMATS = {
        '.txt', '.csv', '.json', '.html', '.htm',
        '.pdf', '.docx', '.odt', '.rtf', '.epub'
    }

    def __init__(self, api_key: str = None):
        """
        Initialize the PersonaAnalyzer.

        Args:
            api_key (str, optional): Anthropic API key. Defaults to environment variable.
        """
        self.client = Anthropic(api_key=api_key)
        self.prompt_template = self._load_prompt_template()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True

    def _load_prompt_template(self) -> str:
        """Load the prompt template from the markdown file."""
        prompt_path = Path(__file__).parent.parent / 'prompt' / 'prompt_persona.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found at {prompt_path}")
            raise

    def _encode_image(self, image_path: Path) -> Dict:
        """Encode an image file to base64."""
        try:
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image: {image_path.name}")
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

    def _extract_text_content(self, file_path: Path) -> str:
        """
        Extract text content from various file formats.

        Args:
            file_path (Path): Path to the file

        Returns:
            str: Extracted text content
        """
        suffix = file_path.suffix.lower()
        try:
            if suffix == '.txt' or suffix == '.rtf':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            elif suffix == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)

            elif suffix == '.docx':
                doc = docx.Document(file_path)
                return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

            elif suffix == '.csv':
                text = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        text.append(','.join(row))
                return '\n'.join(text)

            elif suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.dumps(json.load(f), indent=2)

            elif suffix in {'.html', '.htm'}:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return self.html_converter.handle(f.read())

            elif suffix == '.epub':
                book = epub.read_epub(file_path)
                text = []
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        text.append(self.html_converter.handle(item.get_content().decode('utf-8')))
                return '\n'.join(text)

            elif suffix == '.odt':
                # For ODT files, you might need to implement specific handling
                # or use a library like odfpy
                logger.warning(f"ODT support is limited: {file_path}")
                return f"[Content from ODT file: {file_path.name}]"

            else:
                logger.warning(f"Unsupported file format: {suffix}")
                return f"[Unsupported file format: {file_path.name}]"

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return f"[Error extracting content from: {file_path.name}]"

    def _process_files(self, folder_path: Path) -> Tuple[List[Dict], str]:
        """
        Process all supported files in the folder.

        Args:
            folder_path (Path): Path to the folder containing files

        Returns:
            Tuple[List[Dict], str]: Tuple of (image contents, text contents)
        """
        image_contents = []
        text_contents = []

        for file_path in folder_path.iterdir():
            suffix = file_path.suffix.lower()
            
            if suffix in self.SUPPORTED_IMAGE_FORMATS:
                logger.info(f"Processing image: {file_path.name}")
                image_contents.append(self._encode_image(file_path))
            
            elif suffix in self.SUPPORTED_TEXT_FORMATS:
                logger.info(f"Processing text file: {file_path.name}")
                content = self._extract_text_content(file_path)
                text_contents.append(f"\n=== Content from {file_path.name} ===\n{content}\n")

        return image_contents, '\n'.join(text_contents)

    def analyze_channel(self, images_folder: str | Path) -> str:
        """
        Analyze YouTube channel using files from specified folder.

        Args:
            images_folder (str | Path): Path to folder containing channel data

        Returns:
            str: Analysis results from Claude
        """
        folder_path = Path(images_folder).resolve()
        logger.info(f"Analyzing channel from folder: {folder_path}")
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # Process all files
        image_contents, text_contents = self._process_files(folder_path)

        if not image_contents and not text_contents:
            raise ValueError(f"No supported files found in {folder_path}")

        # Prepare message content
        message_content = image_contents + [{
            'type': 'text',
            'text': f"{text_contents}\n\n{self.prompt_template}"
        }]

        try:
            # Create message using Claude API
            logger.info("Sending request to Claude API...")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.2,
                messages=[{
                    'role': 'user',
                    'content': message_content
                }]
            )
            logger.info("Received response from Claude API")
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