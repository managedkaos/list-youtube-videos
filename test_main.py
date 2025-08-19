"""
Unit tests for YouTube channel scraper
"""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from main import get_channel_videos


class TestGetChannelVideos(unittest.TestCase):
    """Test cases for get_channel_videos function"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"  # nosec
        self.channel_id = "UC123456789"
        self.channel_username = "testchannel"
        self.channel_handle = "@testchannel"
        self.output_filename = "test_output.csv"

    @patch("main.build")
    def test_get_channel_videos_with_channel_id(self, mock_build):
        """Test get_channel_videos with a channel ID"""
        # Mock YouTube API responses
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock channel details response
        mock_youtube.channels().list().execute.return_value = {
            "items": [
                {
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123456789"}},
                    "snippet": {"title": "Test Channel"},
                }
            ]
        }

        # Mock playlist items response
        mock_youtube.playlistItems().list().execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "resourceId": {"videoId": "video123"},
                        "title": "Test Video",
                        "publishedAt": "2023-01-01T00:00:00Z",
                    }
                }
            ],
            "nextPageToken": None,
        }

        # Call the function
        get_channel_videos(self.channel_id, self.api_key, self.output_filename)

        # Verify build was called with correct parameters
        mock_build.assert_called_once_with("youtube", "v3", developerKey=self.api_key)

        # Verify channel details were requested
        mock_youtube.channels().list.assert_called_with(
            part="contentDetails,snippet", id=self.channel_id
        )

        # Verify playlist items were requested
        mock_youtube.playlistItems().list.assert_called_with(
            part="snippet", playlistId="UU123456789", maxResults=50, pageToken=None
        )

    @patch("main.build")
    def test_get_channel_videos_with_username(self, mock_build):
        """Test get_channel_videos with a username"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock username lookup response
        mock_youtube.channels().list().execute.side_effect = [
            # First call for username lookup
            {"items": [{"id": self.channel_id, "snippet": {"title": "Test Channel"}}]},
            # Second call for channel details
            {
                "items": [
                    {
                        "contentDetails": {
                            "relatedPlaylists": {"uploads": "UU123456789"}
                        },
                        "snippet": {"title": "Test Channel"},
                    }
                ]
            },
        ]

        # Mock playlist items response
        mock_youtube.playlistItems().list().execute.return_value = {
            "items": [],
            "nextPageToken": None,
        }

        get_channel_videos(self.channel_username, self.api_key, self.output_filename)

        # Verify username lookup was attempted
        mock_youtube.channels().list.assert_any_call(
            part="contentDetails,snippet", forUsername=self.channel_username
        )

    @patch("main.build")
    def test_get_channel_videos_with_handle(self, mock_build):
        """Test get_channel_videos with a handle (@username)"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock username lookup failure (empty response)
        mock_youtube.channels().list().execute.side_effect = [
            {"items": []},  # Username lookup fails
            # Channel details response
            {
                "items": [
                    {
                        "contentDetails": {
                            "relatedPlaylists": {"uploads": "UU123456789"}
                        },
                        "snippet": {"title": "Test Channel"},
                    }
                ]
            },
        ]

        # Mock search response
        mock_youtube.search().list().execute.return_value = {
            "items": [
                {"snippet": {"channelId": self.channel_id, "title": "Test Channel"}}
            ]
        }

        # Mock playlist items response
        mock_youtube.playlistItems().list().execute.return_value = {
            "items": [],
            "nextPageToken": None,
        }

        get_channel_videos(self.channel_handle, self.api_key, self.output_filename)

        # Verify search was called with handle (without @)
        mock_youtube.search().list.assert_called_with(
            part="snippet", q="testchannel", type="channel", maxResults=1  # @ removed
        )

    @patch("main.build")
    def test_get_channel_videos_channel_not_found(self, mock_build):
        """Test get_channel_videos when channel is not found"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock all lookup methods returning empty results
        mock_youtube.channels().list().execute.return_value = {"items": []}
        mock_youtube.search().list().execute.return_value = {"items": []}

        # This should not raise an exception, just return early
        get_channel_videos("nonexistent", self.api_key, self.output_filename)
        # Function returns None, which is expected behavior

    @patch("main.build")
    def test_get_channel_videos_with_multiple_pages(self, mock_build):
        """Test get_channel_videos with pagination"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock channel details
        mock_youtube.channels().list().execute.return_value = {
            "items": [
                {
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123456789"}},
                    "snippet": {"title": "Test Channel"},
                }
            ]
        }

        # Mock playlist items with pagination
        mock_youtube.playlistItems().list().execute.side_effect = [
            {
                "items": [
                    {
                        "snippet": {
                            "resourceId": {"videoId": "video1"},
                            "title": "Video 1",
                            "publishedAt": "2023-01-01T00:00:00Z",
                        }
                    }
                ],
                "nextPageToken": "token123",
            },
            {
                "items": [
                    {
                        "snippet": {
                            "resourceId": {"videoId": "video2"},
                            "title": "Video 2",
                            "publishedAt": "2023-01-02T00:00:00Z",
                        }
                    }
                ],
                "nextPageToken": None,
            },
        ]

        get_channel_videos(self.channel_id, self.api_key, self.output_filename)

        # Verify playlist items were called multiple times (for pagination)
        # The function calls playlistItems().list() for each page of results
        self.assertGreaterEqual(mock_youtube.playlistItems().list.call_count, 2)

    @patch("main.build")
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.DictWriter")
    def test_get_channel_videos_csv_writing(
        self, mock_csv_writer, mock_file, mock_build
    ):
        """Test that CSV is written correctly"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock channel details
        mock_youtube.channels().list().execute.return_value = {
            "items": [
                {
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123456789"}},
                    "snippet": {"title": "Test Channel"},
                }
            ]
        }

        # Mock playlist items
        mock_youtube.playlistItems().list().execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "resourceId": {"videoId": "video123"},
                        "title": "Test Video",
                        "publishedAt": "2023-01-01T00:00:00Z",
                    }
                }
            ],
            "nextPageToken": None,
        }

        # Mock CSV writer
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance

        get_channel_videos(self.channel_id, self.api_key, self.output_filename)

        # Verify file was opened correctly
        mock_file.assert_called_once_with(
            self.output_filename, "w", newline="", encoding="utf-8"
        )

        # Verify CSV writer was created with correct fieldnames
        mock_csv_writer.assert_called_once_with(
            mock_file(), fieldnames=["Title", "URL", "Published", "Video_ID"]
        )

        # Verify header and data were written
        mock_writer_instance.writeheader.assert_called_once()
        mock_writer_instance.writerow.assert_called_once()

    @patch("main.build")
    def test_get_channel_videos_http_error(self, mock_build):
        """Test get_channel_videos with HTTP error"""
        from googleapiclient.errors import HttpError

        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock HTTP error
        mock_youtube.channels().list().execute.side_effect = HttpError(
            resp=MagicMock(status=403), content=b"Forbidden"
        )

        # This should not raise an exception, just handle the error
        get_channel_videos(self.channel_id, self.api_key, self.output_filename)
        # Function returns None, which is expected behavior

    @patch("main.build")
    def test_get_channel_videos_general_exception(self, mock_build):
        """Test get_channel_videos with general exception"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock general exception
        mock_youtube.channels().list().execute.side_effect = Exception("Test error")

        # This should not raise an exception, just handle the error
        get_channel_videos(self.channel_id, self.api_key, self.output_filename)
        # Function returns None, which is expected behavior

    def test_get_channel_videos_invalid_api_key(self):
        """Test get_channel_videos with invalid API key"""
        # This test verifies the function handles invalid API keys gracefully
        get_channel_videos(self.channel_id, "", self.output_filename)
        # Function returns None, which is expected behavior


if __name__ == "__main__":
    unittest.main()
