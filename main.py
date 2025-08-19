#!/usr/bin/env python3
"""
youtube channel scraper
"""

import csv
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_channel_videos(channel_identifier, api_key, output_filename="youtube_videos.csv"):
    """
    Get all videos from a YouTube channel and save to CSV

    Args:
        channel_identifier: Channel username, handle (@username), or channel ID
        api_key: YouTube Data API key
        output_filename: Output CSV filename
    """

    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        # Try different methods to find the channel
        channel_id = None

        # Method 1: Try as channel ID (starts with UC)
        if channel_identifier.startswith('UC'):
            channel_id = channel_identifier
        else:
            # Method 2: Try as username (legacy)
            try:
                request = youtube.channels().list(
                    part='contentDetails,snippet',
                    forUsername=channel_identifier
                )
                response = request.execute()

                if response['items']:
                    channel_id = response['items'][0]['id']
                    channel_title = response['items'][0]['snippet']['title']
                    print(f"Found channel: {channel_title}")
            except:
                pass

            # Method 3: Try as handle (@username) or search
            if not channel_id:
                # Remove @ if present
                search_term = channel_identifier.lstrip('@')

                # Search for the channel
                search_request = youtube.search().list(
                    part='snippet',
                    q=search_term,
                    type='channel',
                    maxResults=1
                )
                search_response = search_request.execute()

                if search_response['items']:
                    channel_id = search_response['items'][0]['snippet']['channelId']
                    channel_title = search_response['items'][0]['snippet']['title']
                    print(f"Found channel: {channel_title}")

        if not channel_id:
            print(f"Could not find channel: {channel_identifier}")
            return

        # Get channel details to find uploads playlist
        channel_request = youtube.channels().list(
            part='contentDetails,snippet',
            id=channel_id
        )
        channel_response = channel_request.execute()

        if not channel_response['items']:
            print("Channel not found")
            return

        # Get uploads playlist ID
        playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        channel_title = channel_response['items'][0]['snippet']['title']

        print(f"Fetching videos from: {channel_title}")

        # Retrieve all videos from uploads playlist
        videos = []
        next_page_token = None

        while True:
            playlist_items_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            videos.extend(playlist_items_response['items'])

            next_page_token = playlist_items_response.get('nextPageToken')

            if not next_page_token:
                break

            print(f"Fetched {len(videos)} videos so far...")

        # Extract video data
        video_data = []
        for video in videos:
            video_id = video['snippet']['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = video['snippet']['title']
            publish_date = video['snippet']['publishedAt']

            video_data.append({
                'Title': video_title,
                'URL': video_url,
                'Published': publish_date,
                'Video_ID': video_id
            })

        # Write to CSV
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'URL', 'Published', 'Video_ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for video in video_data:
                writer.writerow(video)

        print(f"Successfully saved {len(video_data)} videos to {output_filename}")

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    import sys

    # Check if channel name was provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <channel_name>")
        print("Examples:")
        print("  python script.py DisneyMusicVEVO")
        print("  python script.py @DisneyMusicVEVO")
        print("  python script.py 'UC...' (channel ID)")
        sys.exit(1)

    channel_name = sys.argv[1]

    # Get API key from environment variable
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not API_KEY:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        print("Please set it with: export YOUTUBE_API_KEY='your_api_key_here'")
        sys.exit(1)

    print(f"Fetching videos for channel: {channel_name}")
    get_channel_videos(channel_name, API_KEY, f"{channel_name}_videos.csv")
