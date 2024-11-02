"""
Module for replying to YouTube comments using Claude API.
python -m utility.youtube_comments_reply /Users/yuanlu/Code/youtube_copilot/data/comments
"""
import os
import argparse
from pathlib import Path
from typing import List, Dict
import logging
import json
from anthropic import Anthropic
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommentReplier:
    """
    A class to generate replies for YouTube comments using Claude API.
    """
    def __init__(self, api_key: str = None):
        """
        Initialize the CommentReplier.

        Args:
            api_key (str, optional): Anthropic API key. Defaults to environment variable.
        """
        self.client = Anthropic(api_key=api_key)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load the prompt template from the markdown file."""
        prompt_path = Path(__file__).parent.parent / 'prompt' / 'prompt_persona.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found at {prompt_path}")
            raise

    def _load_comments(self, file_path: Path) -> List[Dict]:
        """
        Load comments from a JSON file.

        Args:
            file_path (Path): Path to the JSON file

        Returns:
            List[Dict]: List of comment dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Log the structure of the loaded data
                logger.debug(f"Loaded data structure: {type(data)}")
                
                # Handle different possible JSON structures
                if isinstance(data, list):
                    if all(isinstance(item, str) for item in data):
                        # Convert simple strings to comment objects
                        return [{'text': comment, 'id': str(i)} for i, comment in enumerate(data)]
                    return data
                elif isinstance(data, dict):
                    # If it's a dictionary with a comments key
                    if 'comments' in data:
                        return data['comments']
                    # If it's a single comment
                    return [data]
                else:
                    raise ValueError(f"Unexpected data format in {file_path}")
        except Exception as e:
            logger.error(f"Error loading comments from {file_path}: {str(e)}")
            raise

    def _generate_reply(self, comment: Dict) -> str:
        """
        Generate a reply for a single comment using Claude API.

        Args:
            comment (Dict): Comment dictionary containing the comment data

        Returns:
            str: Generated reply
        """
        try:
            # Extract comment text based on different possible structures
            comment_text = (
                comment.get('text') or 
                comment.get('comment') or 
                comment.get('content') or 
                comment if isinstance(comment, str) else 
                str(comment)
            )

            # Prepare the prompt with the comment context
            prompt = f"""Based on the following system prompt:

{self.prompt_template}

Please generate a direct, friendly reply for this YouTube comment based on the persona. No explanations or preambles needed:
{comment_text}"""

            # Call Claude API with prefilled response
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {'role': 'user', 'content': prompt},
                    {'role': 'assistant', 'content': '<direct reply>'}  # Prefill to force direct response
                ]
            )
            
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            return f"Error generating reply: {str(e)}"

    def process_comments_file(self, file_path: Path) -> Path:
        """
        Process a single comments file and generate replies.

        Args:
            file_path (Path): Path to the comments JSON file

        Returns:
            Path: Path to the output file with replies
        """
        logger.info(f"Processing comments file: {file_path}")
        
        # Load comments
        comments = self._load_comments(file_path)
        logger.info(f"Loaded {len(comments)} comments")

        # Generate replies for each comment
        processed_comments = []
        for i, comment in enumerate(comments):
            comment_id = comment.get('id', f'comment_{i}')
            logger.info(f"Generating reply for comment ID: {comment_id}")
            
            # Create a structured comment object
            processed_comment = {
                'id': comment_id,
                'original_comment': comment if isinstance(comment, str) else comment.get('text', str(comment)),
                'ai_reply': self._generate_reply(comment)
            }
            processed_comments.append(processed_comment)

        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = file_path.parent / f"{file_path.stem}_replies_{timestamp}.json"

        # Save replies
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_comments, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved replies to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving replies: {str(e)}")
            raise

    def process_folder(self, folder_path: str | Path) -> List[Path]:
        """
        Process all JSON files in the specified folder.

        Args:
            folder_path (str | Path): Path to folder containing comment JSON files

        Returns:
            List[Path]: List of paths to output files with replies
        """
        folder_path = Path(folder_path).resolve()
        logger.info(f"Processing folder: {folder_path}")

        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        # Get all JSON files
        json_files = list(folder_path.glob('*.json'))
        if not json_files:
            raise ValueError(f"No JSON files found in {folder_path}")

        # Process each file
        output_files = []
        for file_path in json_files:
            try:
                output_path = self.process_comments_file(file_path)
                output_files.append(output_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue

        return output_files

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate replies for YouTube comments using Claude API.'
    )
    parser.add_argument(
        'input_folder',
        type=str,
        help='Path to folder containing comment JSON files'
    )
    return parser.parse_args()

def main():
    """Main function to demonstrate usage."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize replier
        replier = CommentReplier()
        
        # Process all files in the folder
        output_files = replier.process_folder(args.input_folder)
        
        # Log results
        logger.info(f"Successfully processed {len(output_files)} files:")
        for file_path in output_files:
            logger.info(f"- {file_path}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main()