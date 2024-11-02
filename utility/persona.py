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

    # Define prompt template directly in code
    PROMPT_TEMPLATE = """
    You are an expert in YouTube content creation and an advisor to the content creator shown in the following screenshots. Analyze the content creator's channel using the provided framework and generate an artifact in markdown format. Your language should be vivid, descriptive, and easy to understand. Strictly follow the framework structure and maintain consistent formatting.

First, carefully examine the following screenshots of the YouTube content creator's channel:

<screenshots>
{{SCREENSHOTS}}
</screenshots>

Now, analyze the content creator's channel using the following framework:

A. Persona
Analyze the content creator's persona by addressing the following points:
A1. Perspective + Age/Gender + Two-word Description
A2. Number of followers
A3. Does creator show own face (if not, take note)
A4. Broad Category
A5. Niche
A6. Level of Expertise in subject matter (rate 1-5 and provide brief evaluation)
A7. Self-Labels (provide 5-6 self-labels)
A8. Linguistic Tone
A9. Personal or brand Image (about 50 words)
A10. Personal Values (about 50 words)
A11. Key Personal Events (if available)
A12. Narrative Structure (rate 1-4)
A13. Aesthetics (briefly describe color schemes, composition methods, and style preferences)
A14. Main Setting/Location
A15. Cultural background / Appearance (if visible or information available)
A16. Language use (if any language other than English is used)

B. Content Strategy / Packaging
Analyze the content creator's strategy and packaging by addressing the following points:
B1. RANK Viral Video Themes (about 100 words, pay attention to view counts)
B2. RANK Viral video examples (list topic, title, and view count for top videos)
B3. How Viral Videos Hit Audience Pain Points (max 5 bullet points, about 50 words total)
B4. Packaging (brief summary of top video idea + topic + thumbnail & title)
B5. List of 10-15 keywords for this content creator to find similar accounts
B6. Calculate average views in creator's channel
B7. Look at number of views on the most popular 5 videos in this creator's channel
B8. Calculate Outlier score for popular videos (views divided by average views)

C. Audience Profile
Analyze the content creator's audience profile by addressing the following points:
C1. Target Audience Age/Gender/Marital Status
C2. Target Audience Region (if known)
C3. Target Audience Educational Background / Occupation
C4. Target Audience Lifestyle
C5. Target Audience specific preferences / subculture

After completing the analysis, format your response as follows:

1. Use markdown formatting for headers and subheaders.
2. Double-check all numbers of views and numbers of followers for accuracy.
3. Provide a short summary of about 300 words at the beginning of the artifact.
4. Ensure that the entire analysis follows the given framework structure.

Present your analysis in a single, cohesive markdown document. Begin with the summary, followed by the detailed analysis under each section (A, B, and C) of the framework.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the PersonaAnalyzer.

        Args:
            api_key (str, optional): Anthropic API key. Defaults to environment variable.
        """
        self.client = Anthropic(api_key=api_key)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True

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
            'text': f"Please analyze this YouTube channel based on the following content:\n\n{text_contents}\n\n{self.PROMPT_TEMPLATE}"
        }]

        try:
            # Create message using Claude API
            logger.info("Sending request to Claude API...")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=5000,
                temperature=0.3,
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