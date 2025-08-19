# YouTube Channel Video Scraper

A Python script that extracts all videos from a YouTube channel and exports them to a CSV file with video titles, URLs, publish dates, and video IDs.

## Features

- **Multiple channel lookup methods**: Works with channel usernames, handles (@username), channel IDs, or search terms
- **Complete video data**: Extracts title, URL, publish date, and video ID
- **Robust CSV output**: Properly handles special characters and commas in video titles
- **Command line interface**: Easy to use from terminal/command prompt
- **Secure API key handling**: Reads API key from environment variables
- **Progress tracking**: Shows fetching progress for large channels
- **Error handling**: Graceful handling of API errors and missing channels

## Prerequisites

- Python 3.6 or higher
- YouTube Data API v3 key from Google Cloud Console
- Required Python package: `google-api-python-client`

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the script is using the pre-built Docker image:

```bash
# Pull the latest image
docker pull ghcr.io/managedkaos/list-youtube-videos:main

# Run with your API key and mount current directory for output
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  <channel_identifier>
```

**Example:**

```bash
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  @DisneyMusicVEVO
```

**Windows Command Prompt:**

```cmd
docker run --rm ^
  -e YOUTUBE_API_KEY=your_api_key_here ^
  -v "%cd%:/work" ^
  ghcr.io/managedkaos/list-youtube-videos:main ^
  @DisneyMusicVEVO
```

**Windows PowerShell:**

```powershell
docker run --rm `
  -e YOUTUBE_API_KEY='your_api_key_here' `
  -v "${PWD}:/work" `
  ghcr.io/managedkaos/list-youtube-videos:main `
  @DisneyMusicVEVO
```

### Option 2: Local Installation

1. **Clone or download the script**

2. **Install required dependencies:**

   ```bash
   pip install google-api-python-client
   ```

3. **Get a YouTube Data API key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API key)
   - Restrict the API key to YouTube Data API v3 (recommended for security)

4. **Set up your API key as an environment variable:**

   **Linux/Mac:**

   ```bash
   export YOUTUBE_API_KEY='your_api_key_here'
   ```

   **Windows Command Prompt:**

   ```cmd
   set YOUTUBE_API_KEY=your_api_key_here  # nosec
   ```

   **Windows PowerShell:**

   ```powershell
   $env:YOUTUBE_API_KEY='your_api_key_here'  # nosec
   ```

   **For permanent setup:**
   - Linux/Mac: Add the export command to your `.bashrc`, `.zshrc`, or equivalent
   - Windows: Add `YOUTUBE_API_KEY` as a system environment variable

## Usage

### Docker Usage (Recommended)

```bash
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  <channel_identifier>
```

> ![Tip]
> When using Docker, the `-v "$(pwd):/work"` flag mounts your current directory to `/work` inside the container.
>
> This ensures that CSV files are saved to your local directory** and persist after the container stops
> Make sure you're in the directory where you want the CSV files to be saved before running the Docker command.

### Local Usage

```bash
python main.py <channel_identifier>
```

### Examples

**Using Docker:**

```bash
# Using channel username (legacy format)
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  DisneyMusicVEVO
```

```bash
# Using channel handle (new format)
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  @DisneyMusicVEVO
```

```bash
# Using channel ID (starts with UC)
docker run --rm \
  -e YOUTUBE_API_KEY='your_api_key_here' \
  -v "$(pwd):/work" \
  ghcr.io/managedkaos/list-youtube-videos:main \
  UC1234567890abcdefg
```

**Using Local Installation:**

```bash
# Using channel username (legacy format)
python main.py DisneyMusicVEVO

# Using channel handle (new format)
python main.py @DisneyMusicVEVO

# Using channel ID (starts with UC)
python main.py UC1234567890abcdefg

# Using search term
python main.py "Disney Music"
```

## Output

The script creates a CSV file named `{channel_name}_videos.csv` with the following columns:

- **Title**: Video title
- **URL**: Full YouTube video URL
- **Published**: Video publish date (ISO format)
- **Video_ID**: YouTube video ID

### Sample Output

```csv
Title,URL,Published,Video_ID
"Let It Go (from Frozen)",https://www.youtube.com/watch?v=L0MK7qz13bU,2013-12-17T16:00:01Z,L0MK7qz13bU
"Circle of Life (from The Lion King)",https://www.youtube.com/watch?v=GibiNy4d4gc,2011-06-23T23:28:49Z,GibiNy4d4gc
```

## Error Handling

The script handles various error scenarios:

- **Missing API key**: Provides instructions for setting up the environment variable
- **Invalid channel**: Shows error message if channel cannot be found
- **API errors**: Displays HTTP error details
- **Missing arguments**: Shows usage instructions

## API Limits

The YouTube Data API v3 has daily quota limits:

- Default quota: 10,000 units per day
- Each playlist items request costs ~3 units
- A channel with 1,000 videos uses approximately 60 units

Monitor your usage in the Google Cloud Console to avoid hitting quota limits.

## Troubleshooting

### Common Issues

#### Docker Issues

1. **"Permission denied" when mounting volume**
   - Ensure you have read/write permissions in the current directory
   - Try running with `sudo` if needed (Linux/Mac)

2. **"No such file or directory" for volume mount**
   - Make sure you're in the correct directory before running the command
   - Use absolute paths if needed: `-v "/full/path/to/directory:work"`

3. **CSV file not appearing in local directory**
   - Check that the volume mount path is correct
   - Verify the container has write permissions to the mounted directory

#### General Issues

1. **"YOUTUBE_API_KEY environment variable not set"**
   - Make sure you've set the environment variable correctly
   - Restart your terminal/command prompt after setting the variable

2. **"Channel not found"**
   - Try different channel identifier formats (@handle, username, channel ID)
   - Verify the channel exists and is public

3. **"quotaExceeded" error**
   - You've hit the daily API quota limit
   - Wait until the quota resets (daily) or increase your quota in Google Cloud Console

4. **Empty CSV file**
   - Channel might have no public videos
   - Check if the channel has an uploads playlist

### Getting Channel Information

If you're unsure about the channel identifier:

- Visit the channel page on YouTube
- Check the URL: `youtube.com/c/ChannelName` or `youtube.com/@ChannelHandle`
- Use the visible channel name or handle as the identifier
