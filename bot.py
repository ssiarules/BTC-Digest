
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
def extract_transcript(youtube_url):
    ydl_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict.get("description", "Transcript not found.")

# Function to summarize text using OpenAI
def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Summarize this transcript:"},
                  {"role": "user", "content": text}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Telegram Command: Start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🚀 Welcome to BTC Digest! Send a YouTube link to get a summary.")

# Telegram Message Handler: Process YouTube Links
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("🔍 Extracting transcript...")
        transcript = extract_transcript(text)
        
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
