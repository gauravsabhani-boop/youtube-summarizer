import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from anthropic import Anthropic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Get credentials from environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Channel IDs - UPDATE THESE WITH ACTUAL IDs
CHANNEL_IDS = [
    'UChpleBmo18P08aKCIgti38g',  # @mreflow - replace with actual ID
    'UCNJ1Ymd5yFuUPtn21xtRbbw',  # @aiexplained-official - replace with actual ID
    'UCHhYXsLBEVVnbvsq57n1MTQ',  # @aiadvantage - replace with actual ID
    'UCbfYPyITQ-7l4upoX8nvctg',  # @TwoMinutePapers - replace with actual ID
    'UCMcoud_ZW7cfxeIugBflSBw',  # @rileybrownai - replace with actual ID
]

class YouTubeSummarizer:
    def __init__(self):
        try:
            self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            print("✅ APIs initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing APIs: {e}")
            sys.exit(1)
    
    def get_recent_videos(self):
        """Fetch videos from last 48 hours"""
        videos = []
        now = datetime.utcnow()
        two_days_ago = now - timedelta(hours=48)
        published_after = two_days_ago.isoformat() + 'Z'
        
        print(f"📥 Searching for videos published after: {published_after}")
        
        for channel_id in CHANNEL_IDS:
            if channel_id.startswith('UCxxxxxx'):
                print(f"⚠️  Skipping {channel_id} - placeholder ID not updated")
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
                print(f"   Found {len(response.get('items', []))} videos from {channel_id}")
            except Exception as e:
                print(f"⚠️  Error fetching from {channel_id}: {e}")
        
        return sorted(videos, key=lambda x: x['published_at'], reverse=True)
    
    def summarize_videos(self, videos):
        """Create AI summary of all videos using Claude"""
        if not videos:
            return "No new videos found in the last 48 hours from the monitored channels."
        
        # Prepare video list for Claude
        video_text = "Here are the videos from the last 48 hours:\n\n"
        for i, video in enumerate(videos, 1):
            video_text += f"{i}. **{video['title']}** by {video['channel']}\n"
            video_text += f"   Published: {video['published_at']}\n"
            description = video['description'][:300] if video['description'] else "No description"
            video_text += f"   Description: {description}...\n\n"
        
        # Ask Claude to summarize
        try:
            print("🧠 Generating summary with Claude AI...")
            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are an expert AI research analyst. Analyze these YouTube videos from AI-focused channels published in the last 48 hours.

Create a CONCISE, professional summary highlighting:
1. Key AI/ML developments or breakthroughs mentioned
2. Novel research techniques or tools discussed
3. Industry trends and patterns
4. What's most important for AI professionals to know
5. Actionable insights

Format: 3-4 paragraphs maximum. Be direct and insightful.

{video_text}"""
                    }
                ]
            )
            
            summary = message.content[0].text
            print("✅ Summary generated successfully")
            return summary
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def send_email(self, summary, videos):
        """Send summary via email"""
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🤖 AI YouTube Summary - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = GMAIL_USER
            msg['To'] = RECIPIENT_EMAIL
            
            # HTML email body
            video_links = ""
            for video in videos:
                video_links += f"""
                <li style="margin-bottom: 12px;">
                    <strong>{video['title']}</strong><br>
                    <small style="color: #666;">Channel: {video['channel']}</small><br>
                    <a href="https://www.youtube.com/watch?v={video['video_id']}" style="color: #1f73b7;">▶ Watch Video</a>
                </li>
                """
            
            html = f"""
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px 8px 0 0; color: white;">
                    <h2 style="margin: 0; font-size: 24px;">📺 AI YouTube Channel Summary</h2>
                </div>
                
                <div style="padding: 20px; background-color: #f8f9fa;">
                    <p style="margin-top: 0; color: #666;">
                        <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}<br>
                        <strong>Videos analyzed:</strong> {len(videos)} from the last 48 hours
                    </p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #667eea;">
                        <h3 style="margin-top: 0; color: #667eea;">📊 Summary</h3>
                        <p style="line-height: 1.8;">{summary.replace(chr(10), '<br>')}</p>
                    </div>
                    
                    <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">🎬 Videos Analyzed</h3>
                    <ul style="list-style: none; padding: 0;">
                        {video_links}
                    </ul>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; margin: 0;">
                        This is an automated summary generated daily at 7:00 AM IST<br>
                        Powered by Claude AI + YouTube API
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            print(f"📧 Sending email to {RECIPIENT_EMAIL}...")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def run_summary(self):
        """Main function to fetch, summarize, and email"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting YouTube Summary at {datetime.now()}")
        print(f"{'='*60}\n")
        
        # Verify credentials
        if not all([YOUTUBE_API_KEY, ANTHROPIC_API_KEY, GMAIL_USER, GMAIL_PASSWORD, RECIPIENT_EMAIL]):
            print("❌ Missing required environment variables!")
            print("   Please set: YOUTUBE_API_KEY, ANTHROPIC_API_KEY, GMAIL_USER, GMAIL_PASSWORD, RECIPIENT_EMAIL")
            return False
        
        # Step 1: Fetch videos
        videos = self.get_recent_videos()
        print(f"\n✅ Total videos found: {len(videos)}\n")
        
        # Step 2: Summarize
        summary = self.summarize_videos(videos)
        
        # Step 3: Send email
        if videos:  # Only send email if there are videos
            self.send_email(summary, videos)
        else:
            print("⚠️  No videos found - email not sent")
        
        print(f"\n{'='*60}")
        print("✅ Summary process completed!")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    summarizer = YouTubeSummarizer()
    summarizer.run_summary()


