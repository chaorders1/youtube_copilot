#!/usr/bin/env python3
"""
Video Improvement Utility

This script compares a new video against baseline popular video advice
to generate specific improvement suggestions.

Usage:
python video_improve.py --baseline "/Users/yuanlu/Code/youtube_copilot/demo/video_analysis_openai_20241102_153021.md" --new "/Users/yuanlu/Code/youtube_copilot/data/frames_output_Claude_Computer_use_for_coding"
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

class VideoImprover:
    """Compares new video against baseline advice to generate improvement suggestions."""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    SUPPORTED_TEXT_FORMATS = {'.txt', '.json', '.vtt', '.md', '.srt'}
    
    def __init__(self, baseline_path: str, new_video_path: str):
        """
        Initialize the VideoImprover.

        Args:
            baseline_path: Path to the baseline video analysis file
            new_video_path: Path to the folder containing new video files
        """
        self.baseline_path = Path(baseline_path)
        self.new_video_path = Path(new_video_path)
        self.processed_files: List[str] = []  # Track processed files
        
    def _encode_image(self, image_path: Path) -> Dict:
        """Encode an image file to base64."""
        try:
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image: {image_path.name}")
                
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
                    # Handle both single objects and arrays
                    if isinstance(content, list):
                        formatted_content = '\n'.join(json.dumps(item, indent=2) for item in content)
                    else:
                        formatted_content = json.dumps(content, indent=2)
                    return f"\n=== {file_path.name} ===\n{formatted_content}\n"
            
            elif suffix in {'.vtt', '.srt'}:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean up subtitle formatting
                    lines = [line for line in content.split('\n') 
                            if not line.strip().isdigit() and 
                            not '-->' in line and 
                            not line.strip().startswith('WEBVTT') and
                            line.strip()]
                    return f"\n=== Transcript from {file_path.name} ===\n{''.join(lines)}\n"
            
            elif suffix in {'.txt', '.md'}:
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

    def _process_files(self) -> Tuple[List[Dict], str, str]:
        """Process baseline analysis and new video files."""
        image_contents = []
        new_video_text = []
        
        # First process baseline analysis
        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Baseline analysis file not found: {self.baseline_path}")
        
        logger.info(f"Processing baseline analysis: {self.baseline_path}")
        baseline_analysis = self._parse_text_file(self.baseline_path)
        self.processed_files.append(str(self.baseline_path))

        # Process new video files recursively
        if not self.new_video_path.exists():
            raise FileNotFoundError(f"New video folder not found: {self.new_video_path}")
        
        # Sort files to ensure consistent processing order
        for file_path in sorted(Path(self.new_video_path).rglob('*')):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                if suffix in self.SUPPORTED_IMAGE_FORMATS:
                    logger.info(f"Processing image: {file_path.name}")
                    try:
                        image_contents.append(self._encode_image(file_path))
                        self.processed_files.append(str(file_path))
                    except Exception as e:
                        logger.error(f"Failed to process image {file_path}: {str(e)}")
                
                elif suffix in self.SUPPORTED_TEXT_FORMATS:
                    logger.info(f"Processing text file: {file_path.name}")
                    new_video_text.append(self._parse_text_file(file_path))
                    self.processed_files.append(str(file_path))

        if not self.processed_files:
            raise ValueError("No supported files found to process")

        logger.info(f"Processed {len(self.processed_files)} files:")
        for file_path in self.processed_files:
            logger.info(f"- {file_path}")

        return image_contents, '\n'.join(new_video_text), baseline_analysis

    def generate_prompt(self) -> str:
        """Generate a comprehensive prompt for improvement analysis."""
        return (
            "You are a video content optimization expert tasked with analyzing a new video "
            "and providing specific improvement suggestions based on successful strategies "
            "from a baseline popular video. Your analysis should be thorough, insightful, "
            "and actionable.\n\n"

            "First, review the baseline successful video analysis:\n\n"

            "<baseline_analysis>\n"
            "{{BASELINE_ANALYSIS}}\n"
            "</baseline_analysis>\n\n"

            "Now, examine the information about the new video:\n\n"

            "<new_video>\n"
            "{{NEW_VIDEO_INFO}}\n"
            "</new_video>\n\n"

            "Your task is to compare the new video against the baseline success factors "
            "and provide detailed improvement suggestions. Structure your analysis as follows:\n\n"

            "<analysis_structure>\n"
            "# Video Improvement Analysis\n\n"

            "## Comments from Viewers Analysis\n\n"

            "## Priority Improvements\n"
            "[For each improvement area:]\n"
            "1. [Improvement Area Name]\n"
            " - Current Approach: [what the new video does]\n"
            " - Successful Strategy: [what the baseline video does]\n"
            " - Specific Suggestions: [3 actionable steps to improve]\n"
            " - Expected Impact: [why this improvement matters]\n\n"

            "## Title Improvement Advice\n"
            "[Provide 3 topic & title ideas for future videos]\n"
            "</analysis_structure>\n\n"

            "For the \"Comments from Viewers Analysis\" section:\n"
            "- Analyze the sentiment and content of viewer comments for both videos\n"
            "- Identify key differences in audience reception\n"
            "- Highlight areas where the new video could improve based on viewer feedback\n\n"

            "For the \"Priority Improvements\" section:\n"
            "- Identify at least 3 key areas where the new video can improve\n"
            "- For each area, clearly state the current approach in the new video and the "
            "successful strategy from the baseline video\n"
            "- Provide 3 specific, actionable suggestions for improvement\n"
            "- Explain the expected impact of each improvement\n\n"

            "For the \"Title Improvement Advice\" section:\n"
            "- Provide 3 topic and title ideas for future videos\n"
            "- Focus on key elements of how the benchmark appealed to its audience\n"
            "- For each idea, include a brief explanation based on the criteria of "
            "authenticity, relatability, and engagement\n"
            "- Emphasize the differences between the profiles and what the audience "
            "responded to in the benchmark profile\n\n"

            "Ensure your suggestions are:\n"
            "- Specific and actionable\n"
            "- Based on evidence from both videos\n"
            "- Prioritized by potential impact\n"
            "- Realistic to implement\n\n"

            "Format your response as a markdown document with clear sections and bullet points. "
            "Use the exact headings and structure provided in the analysis_structure.\n\n"

            "Remember to:\n"
            "- Provide detailed, evidence-based analysis\n"
            "- Focus on actionable improvements\n"
            "- Prioritize suggestions based on potential impact\n"
            "- Maintain a professional and constructive tone throughout\n\n"

            "Begin your analysis now, following the structure and guidelines provided."
        )

    def generate_improvements(self, output_path: Optional[str] = None) -> str:
        """Generate improvement suggestions and save as markdown file.

        Args:
            output_path: Optional path for output file

        Returns:
            Path to the generated markdown file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.new_video_path / f'video_improvements_{timestamp}.md'
        else:
            output_path = Path(output_path)
            
        # Process all files
        image_contents, new_video_text, baseline_analysis = self._process_files()
        
        if not image_contents and not new_video_text:
            raise ValueError("No content found to analyze")
        
        # Prepare message content
        message_content = image_contents + [{
            'type': 'text',
            'text': self.generate_prompt().replace(
                '{{BASELINE_ANALYSIS}}', baseline_analysis
            ).replace(
                '{{NEW_VIDEO_INFO}}', new_video_text
            )
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
            
            improvements = response.content[0].text
            
            # Save the improvements to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(improvements)
                
            logger.info(f"Improvements saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

def main():
    """Main function to handle command line arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description='Generate video improvements based on baseline successful video.'
    )
    parser.add_argument(
        '--baseline',
        required=True,
        help='Path to the baseline video analysis file'
    )
    parser.add_argument(
        '--new',
        required=True,
        help='Path to the folder containing new video files'
    )
    parser.add_argument(
        '--output',
        help='Path for the output markdown file',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        improver = VideoImprover(args.baseline, args.new)
        output_path = improver.generate_improvements(args.output)
        print(f"Improvement analysis completed successfully. Output saved to: {output_path}")
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()