#!/usr/bin/env python3
"""
Video Learning Utility

This script analyzes video-related files (metadata, comments, subtitles, frames)
to generate insights about video popularity on YouTube.

python video_learn.py "/Users/yuanlu/Code/youtube_copilot/data/frames_output_Two_GPT-4os_interacting_and_singing"
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

    def _process_files(self) -> Tuple[List[Dict], str]:
        """
        Process all supported files in the folder.

        Returns:
            Tuple[List[Dict], str]: Tuple of (image contents, text contents)
        """
        image_contents = []
        text_contents = []

        for file_path in self.folder_path.iterdir():
            suffix = file_path.suffix.lower()
            
            if suffix in self.SUPPORTED_IMAGE_FORMATS:
                logger.info(f"Processing image: {file_path.name}")
                image_contents.append(self._encode_image(file_path))
            
            elif suffix in self.SUPPORTED_TEXT_FORMATS:
                logger.info(f"Processing text file: {file_path.name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_contents.append(f"\n=== Content from {file_path.name} ===\n{content}\n")

        return image_contents, '\n'.join(text_contents)

    def generate_prompt(self) -> str:
        """Generate a comprehensive prompt for analysis."""
        return """You are an expert YouTube content analyst. Your task is to analyze the provided video content and explain why it's popular.

Please examine all the provided images (video frames) and text content (metadata, comments, subtitles) to generate a comprehensive analysis.

Your analysis should cover:

1. Content Overview
   - Video topic and main message
   - Production quality assessment
   - Storytelling and pacing analysis

2. Audience Engagement Analysis
   - Comment sentiment and patterns
   - Viewer reactions and engagement indicators
   - Community interaction quality

3. Success Factors
   - Key elements contributing to popularity
   - Unique selling points
   - Content hooks and retention strategies

4. Technical Analysis
   - Title and thumbnail effectiveness
   - SEO and discoverability factors
   - Video length and pacing optimization

5. Recommendations
   - Areas for improvement
   - Content strategy suggestions
   - Growth opportunities

Please format your response in markdown with clear sections, bullet points, and specific examples from the provided content.
"""

    def generate_analysis(self, output_path: Optional[str] = None) -> str:
        """
        Generate analysis and save it as a markdown file using Claude API.
        
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