#!/usr/bin/env python3
"""
Video Learning Utility

This script analyzes video-related files (metadata, comments, subtitles, frames)
to generate insights about video popularity on YouTube.

python video_learn.py "/Users/yuanlu/Code/youtube_copilot/data/frames_output_Two_GPT-4os_interacting_and_singing"
python video_learn.py "/Users/yuanlu/Code/youtube_copilot/data/frames_output_Claude_Computer_use_for_coding"
"""

import argparse
import json
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    """Analyzes video-related files to generate insights about video popularity."""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png'}
    SUPPORTED_TEXT_FORMATS = {'.txt', '.json', '.vtt'}
    
    def __init__(self, folder_path: str):
        """
        Initialize the VideoAnalyzer.

        Args:
            folder_path: Path to the folder containing video-related files
        """
        self.folder_path = Path(folder_path)
        self.metadata: Dict = {}
        self.comments: List[Dict] = []
        self.subtitles: str = ''
        self.frame_paths: List[str] = []
        
    def _encode_image(self, image_path: Path) -> Dict:
        """Encode an image file to base64."""
        try:
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image: {image_path.name}")
                
                # Map file extensions to proper media types
                media_type_mapping = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                
                media_type = media_type_mapping.get(image_path.suffix.lower(), 'image/jpeg')
                
                return {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': media_type,
                        'data': base64_image
                    }
                }
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {str(e)}")
            raise

    def _parse_text_file(self, file_path: Path) -> str:
        """Parse different types of text files appropriately."""
        suffix = file_path.suffix.lower()
        try:
            if suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    return f"\n=== {file_path.name} ===\n{json.dumps(content, indent=2)}\n"
            
            elif suffix == '.vtt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean up VTT formatting
                    lines = [line for line in content.split('\n') 
                            if not line.strip().isdigit() and 
                            not '-->' in line and 
                            line.strip()]
                    return f"\n=== Transcript from {file_path.name} ===\n{''.join(lines)}\n"
            
            elif suffix == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'metadata' in file_path.name.lower():
                        # Parse metadata-style text files
                        metadata = {}
                        for line in content.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
                        return f"\n=== Metadata from {file_path.name} ===\n{json.dumps(metadata, indent=2)}\n"
                    return f"\n=== Content from {file_path.name} ===\n{content}\n"
                
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            return f"\n=== Error parsing {file_path.name} ===\n"

    def _process_files(self) -> Tuple[List[Dict], str]:
        """Process all supported files in the folder and subfolders."""
        image_contents = []
        text_contents = []

        # Process files recursively
        for file_path in Path(self.folder_path).rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                if suffix in self.SUPPORTED_IMAGE_FORMATS:
                    logger.info(f"Processing image: {file_path.name}")
                    try:
                        image_contents.append(self._encode_image(file_path))
                    except Exception as e:
                        logger.error(f"Failed to process image {file_path}: {str(e)}")
                
                elif suffix in self.SUPPORTED_TEXT_FORMATS:
                    logger.info(f"Processing text file: {file_path.name}")
                    text_contents.append(self._parse_text_file(file_path))

        return image_contents, '\n'.join(text_contents)

    def generate_prompt(self) -> str:
        """Generate a comprehensive prompt for analysis."""
        return (
            "You are an expert YouTube content creation advisor. Your task is to "
            "analyze a video based on its transcript, metadata, and screenshots, "
            "and provide a comprehensive evaluation for your client, the content "
            "creator. You will generate an artifact in an MD file that gives your "
            "client an evaluation of this video based on a specific framework.\n\n"
            
            "Here is the video transcript:\n"
            "<video_transcript>\n"
            "{{VIDEO_TRANSCRIPT}}\n"
            "</video_transcript>\n\n"
            
            "Here is the video metadata:\n"
            "<video_metadata>\n"
            "{{VIDEO_METADATA}}\n"
            "</video_metadata>\n\n"
            
            "Here are the video screenshots:\n"
            "<video_screenshots>\n"
            "{{VIDEO_SCREENSHOTS}}\n"
            "</video_screenshots>\n\n"
            
            "Analyze the provided content carefully. Use the transcript to understand "
            "the content and linguistic style, the metadata for quantitative "
            "information, and the screenshots for visual presentation.\n\n"
            
            "Create your evaluation in an MD file format. Structure your analysis "
            "as follows:\n\n"
            
            "# Video Evaluation\n\n"
            
            "## Basic Metrics\n"
            "- Type: [Determine if it's a) Personality/Entertainment Driven, "
            "b) Professional/Educational, or c) Curated/Aggregate]\n"
            "- Area of Interest: [Identify the main topic, e.g., Food, Travel, "
            "Technology, Fashion, Education, Relationships, Gaming]\n"
            "- Subculture or Niche: [Identify any specific subculture or niche]\n"
            "- Creator Self-Label: [Provide 3-5 short phrases that the creator "
            "might use to describe themselves]\n"
            "- Total Views: [Extract from metadata]\n"
            "- Total Likes: [Extract from metadata]\n"
            "- Likes to Views Ratio: [Calculate]\n"
            "- Creator Essence: [Summarize the creator's unique qualities or approach]\n"
            "- Linguistic Style: [Describe, e.g., humorous, serious, warm, thoughtful]\n"
            "- Mission / Value: [Identify the underlying purpose or value "
            "proposition of the content]\n\n"
            
            "## Content Quality Analysis\n"
            "- Clarity: [Evaluate how clear and understandable the content is]\n"
            "- Approachability / Authenticity: [Assess how approachable and "
            "authentic the creator appears]\n"
            "- Approach to Topic: [Analyze how the creator tackles the subject matter]\n"
            "- Audience Alignment: [Evaluate how well the content aligns with "
            "the likely target audience]\n"
            "- Presentation Style: [Describe the overall presentation style "
            "and effectiveness]\n\n"
            
            "For each section, provide a brief explanation or justification for "
            "your evaluation. Use specific examples from the transcript, metadata, "
            "or screenshots to support your points.\n\n"
            
            "When you've completed your analysis, present the entire evaluation "
            "within <md_file> tags. Ensure that your markdown formatting is "
            "correct and consistent throughout the document."
        )

    def generate_analysis(self, output_path: Optional[str] = None) -> str:
        """Generate analysis and save it as a markdown file using Claude API.

        Args:
            output_path: Optional path for the output file. If not provided,
                will create in the same folder as input.

        Returns:
            Path to the generated markdown file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.folder_path / f'video_analysis_{timestamp}.md'
        else:
            output_path = Path(output_path)
            
        # Process all files
        image_contents, text_contents = self._process_files()
        
        # Prepare message content
        message_content = image_contents + [{
            'type': 'text',
            'text': f"Please analyze this YouTube video based on the following content:\n\n{text_contents}\n\n{self.generate_prompt()}"
        }]
        
        try:
            # Initialize Anthropic client
            client = Anthropic()
            
            # Create message using Claude API
            logger.info("Sending request to Claude API...")
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=5000,
                temperature=0.3,
                messages=[{
                    'role': 'user',
                    'content': message_content
                }]
            )
            logger.info("Received response from Claude API")
            
            analysis = response.content[0].text
            
            # Save the analysis to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(analysis)
                
            logger.info(f"Analysis saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

def main():
    """Main function to handle command line arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze video-related files and generate popularity insights.'
    )
    parser.add_argument(
        'folder_path',
        help='Path to the folder containing video-related files'
    )
    parser.add_argument(
        '--output',
        help='Path for the output markdown file',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = VideoAnalyzer(args.folder_path)
        output_path = analyzer.generate_analysis(args.output)
        print(f"Analysis completed successfully. Output saved to: {output_path}")
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()