---
name: video-downloader
description: Download videos and audio from various platforms. Automatically detects platform from URL and checks for res-downloader installation.
---

# Video Downloader Skill

Use this skill when the user wants to download videos, audio, or images from social media platforms.

## Workflow

1. **Check Installation First** - Always verify if res-downloader is installed:
   ```bash
   which res-downloader && res-downloader --help
   ```

2. **Auto-detect Platform** - The tool automatically detects the platform from the URL:
   - Just pass the URL, no need to specify the platform
   - Supported platforms are automatically recognized

3. **Download** - Execute the download command

## Supported Platforms

| Platform | URL Pattern | Notes |
|----------|------------|-------|
| 抖音 (Douyin) | douyin.com | Video download |
| 快手 (Kuaishou) | kuaishou.com | Video download |
| 小红书 (Xiaohongshu) | xiaohongshu.com | Video & images |
| 微信视频号 | WeChat channels | Video download |
| 微信小程序 | WeChat mini programs | Video download |
| B站 (Bilibili) | bilibili.com | Video with quality options |
| YouTube | youtube.com | Video & audio |
| TikTok | tiktok.com | Video download |
| Instagram | instagram.com | Video & images |
| Twitter/X | twitter.com | Video download |
| 微博 (Weibo) | weibo.com | Video download |
| 酷狗音乐 | kugou.com | Audio download |
| QQ音乐 | qq.com | Audio download |
| m3u8 streams | .m3u8 | Video streams |
| Live streams | With proxy | Live recording |

## Usage Commands

```bash
# Basic download - platform auto-detected from URL
res-downloader --url "https://www.douyin.com/..."

# Download to specific directory
res-downloader --url "..." --output ~/Downloads

# Download with proxy (for restricted content)
res-downloader --url "..." --proxy "http://127.0.0.1:7890"

# Download best quality
res-downloader --url "..." --quality best

# Download audio only
res-downloader --url "..." --format mp3
```

## Installation Detection & Setup

### Step 1: Detect Installation
```bash
which res-downloader
# If not found, proceed to install
```

### Step 2: Install Based on OS

**macOS:**
```bash
# Option 1: Homebrew (if available)
brew install res-downloader

# Option 2: Manual download
curl -L -o /tmp/res-downloader.dmg \
  "https://github.com/putyy/res-downloader/releases/download/3.1.3/res-downloader_3.1.3_mac.dmg"
hdiutil attach /tmp/res-downloader.dmg
cp /Volumes/res-downloader/res-downloader.app/Contents/MacOS/res-downloader /usr/local/bin/
hdiutil detach /Volumes/res-downloader
rm /tmp/res-downloader.dmg
```

**Linux (amd64):**
```bash
# Download binary
wget https://github.com/putyy/res-downloader/releases/download/3.1.3/res-downloader_3.1.3_linux_amd64

# Install
chmod +x res-downloader_3.1.3_linux_amd64
sudo mv res-downloader_3.1.3_linux_amd64 /usr/local/bin/res-downloader
```

**Linux (arm64):**
```bash
wget https://github.com/putyy/res-downloader/releases/download/3.1.3/res-downloader_3.1.3_linux_arm64
chmod +x res-downloader_3.1.3_linux_arm64
sudo mv res-downloader_3.1.3_linux_arm64 /usr/local/bin/res-downloader
```

**Windows:**
- Download: https://github.com/putyy/res-downloader/releases/download/3.1.3/res-downloader_3.1.3_win_amd64.exe
- Run the installer

**Build from Source:**
```bash
git clone https://github.com/putyy/res-downloader.git
cd res-downloader
go build
sudo mv res-downloader /usr/local/bin/
```

### Step 3: Verify Installation
```bash
res-downloader --version
# Should output: version 3.1.3
```

## Guidelines

1. **Check first** - Always verify res-downloader is installed before attempting download
2. **Auto-detection** - Don't specify platform, let the tool detect from URL
3. **Report progress** - Inform user about download status
4. **Check disk space** - Warn if file might be large
5. **Respect terms** - Warn about copyright and platform ToS
6. **Use proxy wisely** - Only when content is restricted
7. **Save location** - Use accessible directories like ~/Downloads

## Example Workflows

**Example 1: Download Douyin video**
```
User: "下载这个抖音视频 https://www.douyin.com/..."
Claude:
1. Check: which res-downloader → found
2. Download: res-downloader --url "https://www.douyin.com/..." --output ~/Downloads
3. Report: "已下载到 ~/Downloads/"
```

**Example 2: Linux system without res-downloader**
```
User: "下载B站视频 https://www.bilibili.com/..."
Claude:
1. Check: which res-downloader → not found
2. Install: wget + install command
3. Download: res-downloader --url "..." --output ~/Downloads
```

**Example 3: Download with proxy**
```
User: "下载这个 Instagram 视频，需要代理"
Claude:
1. Check: which res-downloader → found
2. Download: res-downloader --url "..." --proxy "http://127.0.0.1:7890" --output ~/Downloads
```

## Error Handling

- **"res-downloader not found"** → Install it using the appropriate OS command
- **"connection refused"** → Check if the background service is running
- **"platform not supported"** → Inform user and suggest alternatives
- **"download failed"** → Try with proxy or verify URL validity
