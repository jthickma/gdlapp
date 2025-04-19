from flask import Flask, request, send_file
import subprocess
import os
import re

app = Flask(__name__)

DOWNLOAD_DIR = "/downloads"  # Directory to store downloads within the container
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_video_url(url):
    """Heuristic to determine if a URL is likely a video URL."""
    # Basic check for common video platform keywords or patterns
    video_patterns = [
        r"youtube\.com", r"youtu\.be", r"vimeo\.com", r"dailymotion\.com",
        r"twitch\.tv", r"tiktok\.com"
    ]
    for pattern in video_patterns:
        if re.search(pattern, url):
            return True
    return False

@app.route('/')
def index():
    return """
<h1>Media Downloader</h1>
<form action="/download" method="post">
<label for="url">Enter URL:</label>
<input type="text" id="url" name="url" size="50"><br><br>
<input type="submit" value="Download">
</form>
"""

@app.route('/download', methods=['POST'])
def download_media():
    url = request.form.get('url')
    if not url:
        return "No URL provided.", 400

    try:
        if is_video_url(url):
            # Use yt-dlp for video URLs
            result = subprocess.run(['yt-dlp', '--update', '--verbose', '--ignore-errors', '--user-agent', 'Mozilla/5.0', '--trust-server-names', '-o', f'{DOWNLOAD_DIR}/%(title)s.%(ext)s', url], check=True, capture_output=True, text=True)
            print(f"yt-dlp result: {result.returncode}, stdout: {result.stdout}, stderr: {result.stderr}")
            if result.returncode != 0:
                print(f"yt-dlp failed with error: {result.stderr}")
        else:
            # Use gallery-dl for non-video URLs (assuming they are images/galleries)
            result = subprocess.run(['gallery-dl', '--verbose', '--ignore-errors', '--user-agent', 'Mozilla/5.0', '--trust-server-names', '-d', DOWNLOAD_DIR, url], check=True, capture_output=True, text=True)
            print(f"gallery-dl result: {result.returncode}, stdout: {result.stdout}, stderr: {result.stderr}")
            if result.returncode != 0:
                print(f"gallery-dl failed with error: {result.stderr}")

        # Note: This is a simplified approach. In a production environment,
        # you would need logic to determine the actual downloaded filename(s)
        # and potentially archive them or provide a directory listing.
        # For this example, we assume a single file download for demonstration.
        # You would need to inspect the output of yt-dlp or gallery-dl to get the filename.
        # A more robust solution might involve parsing the output or having yt-dlp/gallery-dl
        # output the filename to a known location.
        # For demonstration, let's try to find a file in the download directory
        # This is not reliable for all cases.

        downloaded_files = os.listdir(DOWNLOAD_DIR)
        print(f"Downloaded files: {downloaded_files}")
        if downloaded_files:
            # Assuming the first file found is the one we want to serve
            filepath = os.path.join(DOWNLOAD_DIR, downloaded_files[0])
            print(f"Filepath: {filepath}")
            return send_file(filepath, as_attachment=True)
        else:
            print("No files were found after download.")
            return "Download completed, but no files were found.", 500

    except subprocess.CalledProcessError as e:
        return f"Download failed: {e}", 500
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    