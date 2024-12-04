from screenshot_api import ScreenshotAPI
import concurrent.futures
import time

def bulk_capture(urls, api_token, max_workers=5):
    api = ScreenshotAPI(api_token)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(api.capture, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                filepath = future.result()
                if filepath:
                    print(f"Successfully captured: {url}")
                else:
                    print(f"Failed to capture: {url}")
            except Exception as e:
                print(f"Error capturing {url}: {str(e)}")
            
            # Optional: Add delay to avoid rate limiting
            time.sleep(1)