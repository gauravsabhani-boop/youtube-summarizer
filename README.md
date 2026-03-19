# 🎬 YouTube AI Summarizer - Complete Setup Guide

## 📋 Table of Contents
1. [What You'll Get](#what-youll-get)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Get Your API Keys](#phase-1-get-your-api-keys)
4. [Phase 2: Create GitHub Account & Repository](#phase-2-create-github-account--repository)
5. [Phase 3: Add Files to GitHub](#phase-3-add-files-to-github)
6. [Phase 4: Configure Secrets](#phase-4-configure-secrets)
7. [Phase 5: Update Channel IDs](#phase-5-update-channel-ids)
8. [Phase 6: Test Your Tool](#phase-6-test-your-tool)
9. [Phase 7: Automatic Scheduling](#phase-7-automatic-scheduling)
10. [Troubleshooting](#troubleshooting)

---

## ✨ What You'll Get

✅ **Automated YouTube Monitoring** - Checks 5 YouTube channels automatically
✅ **AI-Powered Summaries** - Claude AI summarizes each video
✅ **Email Reports** - Receives summaries in your inbox every morning at 7 AM IST
✅ **100% Free** - Uses only free tier APIs
✅ **Zero Maintenance** - Runs completely automatically in the cloud
✅ **Multiple Recipients** - Can send to multiple email addresses

---

## 📌 Prerequisites

Before you start, make sure you have:
- A Gmail account (for sending emails)
- A Google account (for YouTube API)
- An Anthropic account (for Claude AI)
- A GitHub account (for automation)
- 30 minutes of your time

---

---

## PHASE 1: Get Your API Keys

### Step 1.1: Get YouTube API Key

1. Go to **https://console.cloud.google.com/**
2. Click **"Select a Project"** (top left)
3. Click **"New Project"**
4. Name it: `YouTubeChannelMonitor`
5. Click **"Create"** and wait 2-3 minutes
6. Search for **"YouTube Data API v3"** in the search bar
7. Click on it and click **"ENABLE"**
8. Go to **"Credentials"** (left sidebar)
9. Click **"Create Credentials"** → **"API Key"**
10. **Copy and save** this key somewhere safe

**✅ Verification:**
- Your key should look like: `AIzaSyD...` (long string)
- Save it in a notepad file

---

### Step 1.2: Get Anthropic API Key

1. Go to **https://console.anthropic.com/**
2. Click **"Sign up"** if you don't have account, or **"Sign in"**
3. Complete signup
4. Go to **"API Keys"** section
5. Click **"Create Key"**
6. Name it: `YouTubeChannelSummarizer`
7. **Copy and save** the key

**✅ Verification:**
- Your key should start with: `sk-ant-...`
- This is your free tier API key

---

### Step 1.3: Create Gmail App Password

1. Go to **https://myaccount.google.com/**
2. Click **"Security"** (left sidebar)
3. **Enable 2-Step Verification** (if not already enabled)
   - Click "2-Step Verification"
   - Follow the steps
4. Search for **"App passwords"** at the top
5. Select **"Mail"** and **"Windows Computer"** (or your device)
6. Google generates a **16-character password**
7. **Copy and save** this password

**✅ Verification:**
- Your password should look like: `qpvl mhqz xabc defg` (16 characters with spaces)
- Write this down - you'll need it later

---

---

## PHASE 2: Create GitHub Account & Repository

### Step 2.1: Create GitHub Account

1. Go to **https://github.com/signup**
2. Enter your email address
3. Create a strong password
4. Choose a username (example: `yourname-youtube-monitor`)
5. Verify your email (check your inbox)

**✅ Verification:**
- You can see your GitHub dashboard
- Your username shows in the top-right corner

---

### Step 2.2: Create New Repository

1. Go to **https://github.com/new**
2. **Repository name:** `youtube-summarizer`
3. **Description:** "Automated YouTube channel summarizer with Claude AI and email notifications"
4. Select **"Public"** (free option)
5. Click **"Create repository"**

**✅ Verification:**
- You see the repository page
- URL shows: `github.com/YOUR_USERNAME/youtube-summarizer`

---

---

## PHASE 3: Add Files to GitHub

### Step 3.1: Add Main Python File

1. Click **"Add file"** → **"Create new file"**
2. **File name:** `youtube_summarizer.py`
3. Paste the following code:

```python
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from anthropic import Anthropic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

CHANNEL_IDS = [
    'UCxxxxxx1',
    'UCxxxxxx2',
    'UCxxxxxx3',
    'UCxxxxxx4',
    'UCxxxxxx5',
]

class YouTubeSummarizer:
    def __init__(self):
        try:
            self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            print("APIs initialized successfully")
        except Exception as e:
            print(f"Error initializing APIs: {e}")
            sys.exit(1)
    
    def get_recent_videos(self):
        videos = []
        now = datetime.utcnow()
        two_days_ago = now - timedelta(hours=48)
        published_after = two_days_ago.isoformat() + 'Z'
        
        print(f"Searching for videos published after: {published_after}")
        
        for channel_id in CHANNEL_IDS:
            if channel_id.startswith('UCxxxxxx'):
                print(f"Skipping {channel_id} - placeholder ID not updated")
                continue
                
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    type='video',
                    order='date',
                    publishedAfter=published_after,
                    maxResults=5
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video = {
                        'title': item['snippet']['title'],
                        'channel': item['snippet']['channelTitle'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'video_id': item['id']['videoId'],
                        'thumbnail': item['snippet']['thumbnails']['high']['url']
                    }
                    videos.append(video)
                print(f"Found {len(response.get('items', []))} videos from {channel_id}")
            except Exception as e:
                print(f"Error fetching from {channel_id}: {e}")
        
        return sorted(videos, key=lambda x: x['published_at'], reverse=True)
    
    def summarize_single_video(self, video):
        """Summarize a single video using Claude - more efficient"""
        try:
            print(f"Summarizing: {video['title'][:50]}...")
            
            prompt = f"""Summarize this YouTube video in 2-3 sentences maximum:

Title: {video['title']}
Channel: {video['channel']}
Description: {video['description']}

Be concise and focus on the key takeaway."""
            
            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            summary = message.content[0].text
            return summary
        except Exception as e:
            print(f"Error summarizing video: {e}")
            return video['description'][:200] if video['description'] else "No summary available"
    
    def run_summary(self):
        print(f"\nStarting YouTube Summary at {datetime.now()}\n")
        
        if not all([YOUTUBE_API_KEY, ANTHROPIC_API_KEY, GMAIL_USER, GMAIL_PASSWORD, RECIPIENT_EMAIL]):
            print("Missing required environment variables!")
            return False
        
        videos = self.get_recent_videos()
        print(f"\nTotal videos found: {len(videos)}\n")
        
        if not videos:
            print("No videos found - email not sent")
            return False
        
        print("Summarizing videos...\n")
        summarized_videos = []
        for video in videos:
            summary = self.summarize_single_video(video)
            summarized_videos.append({
                **video,
                'summary': summary
            })
        
        self.send_email(summarized_videos)
        
        print(f"\nSummary process completed!\n")
    
    def send_email(self, videos):
        try:
            recipients = [email.strip() for email in RECIPIENT_EMAIL.split(',')]
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AI YouTube Summary - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = GMAIL_USER
            msg['To'] = ', '.join(recipients)
            
            video_cards = ""
            for i, video in enumerate(videos, 1):
                video_cards += f"""
                <div style="background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="margin-top: 0; color: #24292f; font-size: 16px;">
                        {i}. {video['title']}
                    </h3>
                    <p style="color: #666; margin: 8px 0; font-size: 13px;">
                        <strong>Channel:</strong> {video['channel']}<br>
                        <strong>Published:</strong> {video['published_at'][:10]}
                    </p>
                    
                    <div style="background: #f6f8fa; padding: 12px; border-radius: 4px; margin: 12px 0; border-left: 3px solid #667eea;">
                        <p style="margin: 0; color: #333; font-size: 14px; line-height: 1.6;">
                            {video['summary']}
                        </p>
                    </div>
                    
                    <a href="https://www.youtube.com/watch?v={video['video_id']}" style="display: inline-block; background: #667eea; color: white; padding: 10px 16px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 10px;">
                        ▶ Watch Video
                    </a>
                </div>
                """
            
            html = f"""<html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 8px; color: white; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 32px;">📺 AI YouTube Channel Summary</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;">Your daily AI-powered video insights</p>
                </div>
                
                <div style="background: #f0f6fc; padding: 16px; border-radius: 6px; margin-bottom: 20px; border-left: 4px solid #0969da;">
                    <p style="margin: 0; color: #0969da; font-weight: bold;">
                        📊 Report Summary
                    </p>
                    <p style="margin: 8px 0 0 0; color: #333; font-size: 14px;">
                        <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}<br>
                        <strong>Videos analyzed:</strong> {len(videos)} from the last 48 hours<br>
                        <strong>Channels monitored:</strong> 5
                    </p>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h2 style="color: #24292f; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px;">🎬 Video Summaries</h2>
                    {video_cards}
                </div>
                
                <hr style="border: none; border-top: 2px solid #ddd; margin: 30px 0;">
                
                <div style="background: #f8f9fa; padding: 16px; border-radius: 6px; text-align: center;">
                    <p style="margin: 0; color: #666; font-size: 12px;">
                        <strong>Automated Summary Report</strong><br>
                        Sent daily at 7:00 AM IST<br>
                        Powered by Claude AI + YouTube API<br><br>
                        <a href="https://github.com/gauravsabhani-boop/youtube-summarizer" style="color: #667eea; text-decoration: none;">View on GitHub</a>
                    </p>
                </div>
            </body></html>"""
            
            msg.attach(MIMEText(html, 'html'))
            
            print(f"Sending email to {len(recipients)} recipient(s)...")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.send_message(msg)
            
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

if __name__ == "__main__":
    summarizer = YouTubeSummarizer()
    summarizer.run_summary()
```

4. Scroll down and click **"Commit changes"**
5. Click **"Commit changes"** again in the popup

**✅ Verification:**
- You see `youtube_summarizer.py` in your repository

---

### Step 3.2: Add Workflow Scheduler File

1. Click **"Add file"** → **"Create new file"**
2. **File name:** `.github/workflows/schedule.yml`
3. Paste the following code:

```yaml
name: Daily YouTube Summary Report

on:
  schedule:
    # Runs at 1:30 AM UTC which is 7:00 AM IST (IST is UTC+5:30)
    - cron: '30 1 * * *'
  workflow_dispatch:  # Allows manual trigger from GitHub UI

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  summarize:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic
      
      - name: Run YouTube Summarizer
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_USER: ${{ secrets.GMAIL_USER }}
          GMAIL_PASSWORD: ${{ secrets.GMAIL_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
        run: python youtube_summarizer.py
```

4. Scroll down and click **"Commit changes"**
5. Click **"Commit changes"** again

**✅ Verification:**
- You see `.github/workflows/schedule.yml` in your repository

---

---

## PHASE 4: Configure Secrets

### Step 4.1: Add Your Secret Keys

1. Go to your repository
2. Click **"Settings"** (top menu)
3. Click **"Secrets and variables"** → **"Actions"** (left sidebar)
4. Click **"New repository secret"**

### Add 5 Secrets (One by one):

**Secret 1: YOUTUBE_API_KEY**
- Name: `YOUTUBE_API_KEY`
- Value: Your YouTube API key (from Phase 1.1)
- Click "Add secret"

**Secret 2: ANTHROPIC_API_KEY**
- Click "New repository secret"
- Name: `ANTHROPIC_API_KEY`
- Value: Your Anthropic key (from Phase 1.2)
- Click "Add secret"

**Secret 3: GMAIL_USER**
- Click "New repository secret"
- Name: `GMAIL_USER`
- Value: Your Gmail address (example: `your_email@gmail.com`)
- Click "Add secret"

**Secret 4: GMAIL_PASSWORD**
- Click "New repository secret"
- Name: `GMAIL_PASSWORD`
- Value: Your 16-character Gmail app password (from Phase 1.3)
- Click "Add secret"

**Secret 5: RECIPIENT_EMAIL**
- Click "New repository secret"
- Name: `RECIPIENT_EMAIL`
- Value: Email address(es) to receive summaries
  - Single email: `your_email@gmail.com`
  - Multiple emails: `email1@gmail.com, email2@gmail.com, email3@gmail.com`
- Click "Add secret"

**✅ Verification:**
- You see all 5 secrets listed:
  - ✅ YOUTUBE_API_KEY
  - ✅ ANTHROPIC_API_KEY
  - ✅ GMAIL_USER
  - ✅ GMAIL_PASSWORD
  - ✅ RECIPIENT_EMAIL

---

---

## PHASE 5: Update Channel IDs

### Step 5.1: Find Your YouTube Channel IDs

For each of the 5 channels, do this:

1. Visit the channel (e.g., https://www.youtube.com/@mreflow)
2. Right-click on the page → **"View Page Source"** (or press `Ctrl+U` / `Cmd+U`)
3. Press `Ctrl+F` / `Cmd+F` and search: `"externalId":"UC`
4. You'll see something like: `"externalId":"UC1234567890abcdefghijklmn"`
5. Copy the ID: `UC1234567890abcdefghijklmn` (24 characters starting with UC)

**Your 5 Channel IDs:**
- @mreflow: `UC...`
- @aiexplained-official: `UC...`
- @aiadvantage: `UC...`
- @TwoMinutePapers: `UC...`
- @rileybrownai: `UC...`

---

### Step 5.2: Update in GitHub

1. Go to your repository
2. Click on `youtube_summarizer.py`
3. Click the pencil icon (✏️) to edit
4. Find this section (around line 13):

```python
CHANNEL_IDS = [
    'UCxxxxxx1',
    'UCxxxxxx2',
    'UCxxxxxx3',
    'UCxxxxxx4',
    'UCxxxxxx5',
]
```

5. Replace with your actual IDs:

```python
CHANNEL_IDS = [
    'UC1234567890abcdefghijklmn',  # @mreflow
    'UC2234567890abcdefghijklmn',  # @aiexplained-official
    'UC3234567890abcdefghijklmn',  # @aiadvantage
    'UC4234567890abcdefghijklmn',  # @TwoMinutePapers
    'UC5234567890abcdefghijklmn',  # @rileybrownai
]
```

6. Click **"Commit changes"**
7. Click **"Commit changes"** again

**✅ Verification:**
- Each ID is 24 characters
- Each ID starts with UC
- All 5 channels are listed

---

---

## PHASE 6: Test Your Tool

### Step 6.1: Manual Test Run

1. Go to your repository
2. Click **"Actions"** tab (top menu)
3. Click **"Daily YouTube Summary Report"** (left sidebar)
4. Click **"Run workflow"** button (top right)
5. Click the green **"Run workflow"** button
6. GitHub will start running your tool

### Step 6.2: Monitor the Run

1. You should see a new run appear
2. It will show a **yellow circle** (⏳ running)
3. Wait 2-3 minutes for it to complete
4. It should turn **GREEN ✅** if successful

### Step 6.3: Check Your Email

1. Open your email inbox
2. Check for an email with subject: `AI YouTube Summary - [Date]`
3. You should see:
   - Videos found from your channels
   - AI summary for each video (2-3 sentences)
   - Channel name for each video
   - "Watch Video" link for each one

**✅ Verification:**
- ✅ Workflow shows GREEN ✅
- ✅ Email received in inbox
- ✅ Email contains video summaries
- ✅ Email has watch links

---

### Troubleshooting Tests

**If workflow shows RED ❌:**
1. Click on the failed run
2. Click "summarize" job
3. Look for red error messages
4. Check [Troubleshooting](#troubleshooting) section

**If you don't get an email:**
1. Check spam folder
2. Verify GMAIL_PASSWORD is exactly 16 characters
3. Verify GMAIL_USER is correct
4. Check workflow errors (step above)

---

---

## PHASE 7: Automatic Scheduling

### Step 7.1: How It Works

Your tool is already scheduled to run **every day at 7:00 AM IST** automatically!

The workflow file `.github/workflows/schedule.yml` contains:
```yaml
schedule:
  - cron: '30 1 * * *'  # 1:30 AM UTC = 7:00 AM IST
```

This means:
- ✅ Every morning at 7:00 AM IST
- ✅ GitHub automatically runs your tool
- ✅ Emails are sent to your recipients
- ✅ You don't have to do anything!

### Step 7.2: Monitor Runs

1. Go to **Actions** tab anytime
2. You'll see all past runs
3. Each day a new run should appear at 7:00 AM IST
4. Click any run to see details

### Step 7.3: Manual Trigger

You can also run it manually anytime:
1. Go to **Actions**
2. Click **"Daily YouTube Summary Report"**
3. Click **"Run workflow"**
4. Click green **"Run workflow"** button
5. It runs immediately (within 1 minute)

---

---

## 📚 How to Add More Email Recipients

Want to send summaries to more people?

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Find **RECIPIENT_EMAIL**
3. Click the **edit button** (pencil icon)
4. Change the value to:
   ```
   email1@gmail.com, email2@gmail.com, email3@gmail.com
   ```
5. Click **"Update secret"**

Next run will send to all 3 emails!

---

---

## 💡 Cost Analysis (100% FREE!)

| Item | Cost | Notes |
|------|------|-------|
| YouTube API | $0 | Free tier: 10,000 requests/day (you use ~5) |
| Anthropic Claude | $0 | Free tier: ~50,000 tokens/month (~30 used) |
| Gmail SMTP | $0 | Free for sending emails |
| GitHub Actions | $0 | Free tier includes 2,000 minutes/month |
| **TOTAL** | **$0** | Runs forever for free! |

---

---

## 🔧 Troubleshooting

### Problem: Workflow shows RED ❌

**Solution:**
1. Click the failed run
2. Click "summarize" job
3. Look for error messages
4. Most common errors:
   - `Invalid API key` → Check your secrets are correct
   - `Authentication failed` → Check GMAIL_PASSWORD format
   - `Channel ID invalid` → Verify UC... IDs are 24 characters
   - `No videos found` → Channels haven't posted in 48 hours (this is OK!)

---

### Problem: Emails not received

**Solution:**
1. Check spam/promotions folder
2. Verify RECIPIENT_EMAIL is correct
3. Try running manually to test
4. Check your GMAIL_USER and GMAIL_PASSWORD match

---

### Problem: "Your credit balance is too low"

**Solution:**
Anthropic gives free credits. If you run out:
1. Go to https://console.anthropic.com/
2. Go to Billing
3. Click "Buy credits"
4. Add $5 (will last months)

OR wait for next month - free credits reset monthly!

---

### Problem: "Placeholder ID not updated"

**Solution:**
Your channel IDs still contain `UCxxxxxx`. Update them:
1. Go to `youtube_summarizer.py`
2. Edit the CHANNEL_IDS section
3. Replace with actual UC... IDs
4. Commit changes

---

---

## 📞 Support & Resources

- **GitHub Issues:** Use GitHub repo Issues tab for bugs
- **YouTube API Docs:** https://developers.google.com/youtube/v3
- **Anthropic Docs:** https://docs.anthropic.com/
- **GitHub Actions Docs:** https://docs.github.com/actions

---

---

## 🎉 You're All Set!

Your YouTube Summarizer is now:
✅ Running automatically every day at 7 AM IST
✅ Finding videos from 5 AI YouTube channels
✅ Summarizing with Claude AI
✅ Sending beautiful emails with summaries
✅ 100% FREE
✅ Zero maintenance

Enjoy your daily AI YouTube summaries! 🚀📺

---

**Last Updated:** March 19, 2026
**Version:** 1.0
