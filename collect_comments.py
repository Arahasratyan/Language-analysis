import yt_dlp
import csv
import os
import sys
import time
import re
from typing import List, Dict
from datetime import datetime


class YouTubeCommentExtractor:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'getcomments': True,  # Enable comment extraction
            'skip_download': True,  # Don't download the video
        }
    
    def timestamp_to_date(self, timestamp: int) -> str:
        """Convert Unix timestamp to date only (YYYY-MM-DD)"""
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return 'N/A'
    
    def extract_video_id(self, video_url: str) -> str:
        """Extract video ID from URL"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get('id', 'unknown')
        except Exception as e:
            print(f"Error extracting video ID: {e}")
            return 'unknown'
    
    def extract_comments(self, video_url: str) -> List[Dict]:
        """
        Extract comments from a YouTube video using yt-dlp
        
        Args:
            video_url: YouTube video URL or video ID
        
        Returns:
            List of comment dictionaries
        """
        print(f"Extracting comments from: {video_url}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract video info including comments
                info = ydl.extract_info(video_url, download=False)
                
                video_id = info.get('id', 'unknown')
                
                if 'comments' not in info or not info['comments']:
                    print(f"  No comments found for video {video_id}")
                    return []
                
                raw_comments = info['comments']
                
                # Parse and structure comment data
                all_comments = []
                for comment in raw_comments:
                    comment_data = {
                        'video_id': video_id,
                        'date': self.timestamp_to_date(comment.get('timestamp', 0)),
                        'text': comment.get('text', ''),
                        'like_count': comment.get('like_count', 0),
                        'is_reply': comment.get('parent') != 'root',
                        'parent_id': comment.get('parent', 'root'),
                        'comment_id': comment.get('id', ''),
                    }
                    all_comments.append(comment_data)
                
                # Separate top-level comments and replies
                top_level_comments = [c for c in all_comments if not c['is_reply']]
                all_replies = [c for c in all_comments if c['is_reply']]
                
                # Count replies for each top-level comment
                for comment in top_level_comments:
                    reply_count = sum(1 for reply in all_replies if reply['parent_id'] == comment['comment_id'])
                    comment['reply_count'] = reply_count
                
                # Set reply_count to -1 for all replies
                for reply in all_replies:
                    reply['reply_count'] = -1
                
                # Combine all comments
                final_comments = top_level_comments + all_replies
                
                print(f"  Extracted {len(top_level_comments)} top-level comments and {len(all_replies)} replies")
                
                return final_comments
                
        except Exception as e:
            print(f"Error extracting comments: {e}")
            return []


def get_channel_video_urls(channel_url: str, max_videos: int = None) -> List[str]:
    """
    Get all video URLs from a YouTube channel
    
    Args:
        channel_url: YouTube channel URL (e.g., https://www.youtube.com/@ChannelName/videos)
        max_videos: Maximum number of videos to fetch (None = all)
    
    Returns:
        List of video URLs
    """
    # Validate and fix YouTube URL
    if not re.match(r'https?://(www\.)?youtube\.com/@[\w-]+(/videos)?', channel_url):
        if '@' in channel_url and '/videos' not in channel_url:
            channel_url = channel_url.rstrip('/') + '/videos'
        else:
            raise ValueError(
                "Invalid YouTube channel URL. Format should be: https://www.youtube.com/@ChannelName/videos")

    # Configure yt-dlp
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
        'ignoreerrors': True,
        'playlist_items': f'1:{max_videos}' if max_videos else None,
        'skip_download': True,
        'no_warnings': True,
    }

    video_urls = []

    try:
        print(f"⏳ Starting collection from {channel_url}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)

            if not result or 'entries' not in result:
                print("❌ No videos found. Check the channel URL and ensure it's accessible.")
                return []

            # Get entries
            entries = list(result.get('entries', []))
            total_videos = len(entries)
            print(f"🔍 Found {total_videos} videos to process")

            # Process videos
            for idx, entry in enumerate(entries, 1):
                if not entry:
                    continue

                # Get video ID and create URL
                video_id = entry.get('id')
                if video_id:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_urls.append(video_url)

                # Progress update
                if idx % 50 == 0 or idx == total_videos:
                    print(f"✅ Processed {idx}/{total_videos} videos ({(idx / total_videos) * 100:.1f}%)")

                # Add small delay to prevent rate limiting for very large channels
                if idx % 500 == 0:
                    time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

    if video_urls:
        print(f"\n🎉 Successfully collected {len(video_urls)} video URLs")
    else:
        print("\n❌ No video URLs collected")
    
    return video_urls


def process_multiple_videos(video_urls: List[str], output_filename: str = 'all_comments.csv'):
    """
    Process multiple videos and save all comments to a single CSV file
    If the file exists, comments are appended; otherwise, a new file is created.
    
    Args:
        video_urls: List of YouTube video URLs
        output_filename: Name of the output CSV file
    """
    extractor = YouTubeCommentExtractor()
    
    # Check if file exists to determine write mode
    file_exists = os.path.isfile(output_filename)
    mode = 'a' if file_exists else 'w'
    
    if file_exists:
        print(f"📄 File '{output_filename}' exists. Appending new comments...\n")
    else:
        print(f"📄 Creating new file '{output_filename}'...\n")
    
    # Open CSV file for writing/appending
    with open(output_filename, mode, newline='', encoding='utf-8') as f:
        fieldnames = ['video_id', 'date', 'text', 'like_count', 'reply_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header only if creating new file
        if not file_exists:
            writer.writeheader()
        
        total_comments = 0
        total_replies = 0
        
        # Process each video
        for i, video_url in enumerate(video_urls, 1):
            print(f"\n[{i}/{len(video_urls)}] Processing video: {video_url}")
            
            comments = extractor.extract_comments(video_url)
            
            # Write comments to CSV
            for comment in comments:
                writer.writerow({
                    'video_id': comment['video_id'],
                    'date': comment['date'],
                    'text': comment['text'].replace('\n', ' ').replace('\r', ' '),
                    'like_count': comment['like_count'],
                    'reply_count': comment['reply_count'],
                })
                
                if comment['reply_count'] == -1:
                    total_replies += 1
                else:
                    total_comments += 1
        
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Total videos processed: {len(video_urls)}")
        print(f"Total top-level comments: {total_comments}")
        print(f"Total replies: {total_replies}")
        print(f"Total rows added to CSV: {total_comments + total_replies}")
        print(f"Output file: {output_filename}")
        print(f"Mode: {'Appended' if file_exists else 'Created new file'}")
        print("="*80)


def process_channel_comments(channel_url: str, output_filename: str = 'all_comments.csv', max_videos: int = None):
    """
    Process all videos from a channel and extract their comments
    
    Args:
        channel_url: YouTube channel URL
        output_filename: Name of the output CSV file
        max_videos: Maximum number of videos to process (None = all)
    """
    print("="*80)
    print("YOUTUBE CHANNEL COMMENT EXTRACTOR")
    print("="*80)
    
    # Get all video URLs from the channel
    video_urls = get_channel_video_urls(channel_url, max_videos)
    
    if not video_urls:
        print("No videos found to process.")
        return
    
    print("\n" + "="*80)
    print("STARTING COMMENT EXTRACTION")
    print("="*80)
    
    # Process all videos and extract comments
    process_multiple_videos(video_urls, output_filename)


# Example usage
if __name__ == "__main__":
    # ===== OPTION 1: Process specific video URLs =====
    # video_urls = [
    #     "https://youtu.be/q9zbc-ToCNE",
    #     "https://www.youtube.com/watch?v=VIDEO_ID_2",
    #     "https://www.youtube.com/watch?v=VIDEO_ID_3",
    # ]
    # process_multiple_videos(video_urls, output_filename='all_comments.csv')
    
    # ===== OPTION 2: Process entire channel =====
    channel_url = "https://www.youtube.com/@ChannelName/videos"  # Replace with actual channel
    process_channel_comments(
        channel_url=channel_url,
        output_filename='all_comments.csv',
        max_videos=None  # Set to a number to limit videos, or None for all
    )
    
    # ===== OPTION 3: Command line usage =====
    # Uncomment this section to use command line arguments
    # if len(sys.argv) > 1:
    #     if sys.argv[1].startswith('@'):
    #         # Channel URL provided
    #         channel = sys.argv[1]
    #         output = sys.argv[2] if len(sys.argv) > 2 else 'all_comments.csv'
    #         max_vids = int(sys.argv[3]) if len(sys.argv) > 3 else None
    #         process_channel_comments(channel, output, max_vids)
    #     else:
    #         print("Usage: python script.py <CHANNEL_URL> [OUTPUT_FILE] [MAX_VIDEOS]")
    #         print("Example: python script.py 'https://www.youtube.com/@ChannelName/videos' comments.csv 100")