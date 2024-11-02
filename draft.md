** # Project overview **
This is prepared for Claude day. Youtubers can use this to brainstrom their project ideas.


** # Core functionalities **

### Youtube video download
1. Download videos using yt-dlp library with flexible options:
   - Video formats: MP4, WebM, audio-only
   - Quality options: 4K, 1080p, 720p, 480p, 360p
   - Optional subtitle downloads in multiple languages
   - Sanitized filenames for system compatibility

2. Command line usage examples:
   ```bash
   # Basic video download in MP4 format
   python youtube_video_download.py url='https://www.youtube.com/watch?v=VIDEO_ID'

   # Download with specific quality
   python youtube_video_download.py url='https://www.youtube.com/watch?v=VIDEO_ID' quality='720p'

   # Download audio only
   python youtube_video_download.py url='https://www.youtube.com/watch?v=VIDEO_ID' format='audio'

   # Download with English subtitles
   python youtube_video_download.py url='https://www.youtube.com/watch?v=VIDEO_ID' subtitles='en'
   ```
   

3. Output Structure:
   ```
   data/youtube_video/
   ├── video_title.mp4           # Downloaded video file
   ├── video_title.en.vtt        # English subtitles (if requested)
   └── video_title.mp3           # Audio-only file (if audio format selected)
   ```

4. Features:
   - Automatic filename sanitization (removes special characters)
   - Progress tracking during download
   - Detailed logging of download process
   - Support for multiple quality options
   - Flexible format selection
   - Subtitle download capability

5. Dependencies:
   - Python 3.6+
   - yt-dlp library
   - FFmpeg (for audio extraction and subtitle conversion)

### Video frame split
1. Extract frames from video files at specified intervals using OpenCV:
   - Save frames as JPEG images with detailed metadata
   - Support various video formats (MP4, AVI, MOV)
   - Track extraction progress
   - Generate comprehensive metadata file

2. Command line usage examples:
   ```bash
   # Basic usage - extract every frame
   python video_frame_split.py "path/to/video.mp4"

   # Extract frames every 10 seconds with custom output directory
   python video_frame_split.py "path/to/video.mp4" frames_output 10.0
   ```

3. Output Structure:
   ```
   data/frames_output/
   ├── metadata.txt                      # Extraction metadata and video info
   ├── timestamp_000000_frame_0000_time_0.0s.jpg
   ├── timestamp_000010_frame_0300_time_10.0s.jpg
   └── ...
   ```

4. Features:
   - Frame extraction at specified time intervals
   - Detailed metadata generation including:
     - Video properties (resolution, FPS, duration)
     - Extraction settings
     - File naming conventions
     - Processing timestamps
   - Progress tracking and logging
   - Organized output structure
   - Timestamp and frame number in filenames

5. Dependencies:
   - Python 3.6+
   - OpenCV (cv2)

6. Metadata File Contents:
   - Source video information
   - Video properties (codec, resolution, FPS)
   - Extraction settings
   - File naming convention details
   - Processing date and time


### Youtube screenshot (Difficult to get. Wait)
1. Use pikwy to take screenshot of a given youtube video url
2. Save the screenshot to the data folder


### Youtube channel persona analysis
1. Assume we have the screenshot of youtube channel video tab
2. Use picture_crop.py to split the screenshot into 1024 x 1024 images
3. use @prompt/prompt_full_analysis_102524.md to analyze the screenshot
4. Save the analysis to the data folder as persona_analysis.md

### Youtube video comment reply
1. Use apify or chrome extension to get the comment data in json format like @data/claude___computer_use_for_coding-comments.json
2. use persona prompt and @prompt/prompt_comment_reply_102524.md to analyze the comment data
3. Save the analysis to the data folder as comment_reply_analysis.md

### Youtube video full analysis
1. Use youtube api to get the audio and video of a given youtube video
2. Get transcript of the video either from youtube directly or get transcribed from audio
3. Use python library cv2 to take screenshot of the video frame by frame
4. Upload the video frames ( 50 frames for example) and transcript to Claude
5. Claude will generate a video analysis

### Find similar youtube videos
1. You will be given a youtube video url
2. Use chrome icognito mode and open the youtube video url


### Competitor video analysis
1. You will be given a youtube video url
2. Use chrome icognito mode and open the youtube video url
3. Get the related videos from the youtube video


** # Doc **
*** Target youtube channel for test
https://www.youtube.com/@anthropic-ai
*** libraries
*** api code example
                    import anthropic

                    client = anthropic.Anthropic(
                        # defaults to os.environ.get("ANTHROPIC_API_KEY")
                        api_key="my_api_key",
                    )
                    message = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        messages=[
                            {"role": "user", "content": "Hello, Claude"}
                        ]
                    )
                    print(message.content)

** # Current file structure **
xxxxx

** # Additional requirements **
xxxxx