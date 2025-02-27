
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
import yt_dlp

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Function to extract YouTube transcript
import yt_dlp

def extract_transcript(youtube_url):
    ydl_opts = {
        "quiet": True,
        "writesubtitles": True,
        "subtitleslangs": ["en"],  # English subtitles
        "skip_download": True,
        "writeautomaticsub": True  # Fallback to auto-generated subtitles
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        subtitles = info_dict.get("subtitles", {})
        auto_subs = info_dict.get("automatic_captions", {})

        # Get manually provided subtitles first, fallback to auto-generated
        transcript_url = None
        if "en" in subtitles:
            transcript_url = subtitles["en"][0]["url"]
        elif "en" in auto_subs:
            transcript_url = auto_subs["en"][0]["url"]

        return transcript_url or "Transcript not available."

# Function to summarize text using OpenAI
from openai import OpenAI
import os

# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to summarize text using OpenAI GPT-4
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # ✅ Correct model name
        messages=[
            {"role": "system", "content": "Summarize this transcript:"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()



# Telegram Command: Start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🚀 Welcome to BTC Digest! Send a YouTube link to get a summary.")

# Telegram Message Handler: Process YouTube Links
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("🔍 Extracting transcript...")

        transcript = extract_transcript(text)
        if transcript == "Transcript not available.":
            await update.message.reply_text("❌ Could not retrieve transcript.")
            return

        await update.message.reply_text("📝 Summarizing...")
        
        summary = summarize_text(transcript)

        await update.message.reply_text(f"✅ Summary:\n\n{summary}")
    else:
        await update.message.reply_text("❌ Please send a valid YouTube link.")

# Main function to run the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
