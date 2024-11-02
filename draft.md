** # Project overview **
This is prepared for Claude day. Youtubers can use this to brainstrom their project ideas.


** # Core functionalities **
### Youtube channel persona analysis
1. Use apify to take screenshot of youtube channel
2. Take screenshot of youtube channel video tab (here does not find apify actor)
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


### Youtube video download
1. Use yt-dlp to download the youtube video and save to the "data/youtube_video" folder
1.1 Reference of this package is https://github.com/yt-dlp/yt-dlp



** # Doc **
*** Target youtube channel for test
https://www.youtube.com/@anthropic-ai
*** libraries
*** api code example

** # Current file structure **
xxxxx

** # Additional requirements **
xxxxx