
import os
import time
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
import yt_dlp

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Function to extract YouTube transcript
def extract_transcript(youtube_url):
    ydl_opts = {
        "quiet": True,
        "writesubtitles": True,
        "subtitleslangs": ["en"],
        "skip_download": True,
        "writeautomaticsub": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        subtitles = info_dict.get("subtitles", {})
        auto_subs = info_dict.get("automatic_captions", {})

        transcript_url = None
        if "en" in subtitles:
            transcript_url = subtitles["en"][0]["url"]
        elif "en" in auto_subs:
            transcript_url = auto_subs["en"][0]["url"]

        if transcript_url:
            # Fetch the transcript content
            response = requests.get(transcript_url)
            if response.status_code == 200:
                return response.text  # Return transcript as plain text
            else:
                return "❌ Error retrieving transcript."

        return "Transcript not available."

# Function to split large text into chunks for OpenAI processing
def split_into_chunks(text, chunk_size=2000):
    chunks = []
    while len(text) > chunk_size:
        split_index = text.rfind(' ', 0, chunk_size)
        chunks.append(text[:split_index])
        text = text[split_index:].strip()
    chunks.append(text)  # Add the remaining text as the last chunk
    return chunks

# Function to summarize text using the new OpenAI API (v1.0.0+)
def summarize_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo" if you want a cheaper model
            messages=[
                {"role": "system", "content": "Summarize the following text:"},
                {"role": "user", "content": text}
            ],
            max_tokens=150,  # You can adjust the max tokens as needed
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()  # Extract summary text from the response
    except openai.error.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "❌ There was an error while summarizing the text. Please try again later."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "❌ An unexpected error occurred. Please try again later."

# Telegram Command: Start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🚀 Welcome to BTC Digest! Send a YouTube link to get a summary.")

# Telegram Message Handler: Process YouTube Links
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("🔍 Extracting transcript...")

        # Extract transcript from the YouTube link
        transcript = extract_transcript(text)

        if transcript == "Transcript not available.":
            await update.message.reply_text("❌ Could not retrieve transcript.")
            return

        # Split the transcript into smaller chunks
        chunks = split_into_chunks(transcript)

        # Summarize each chunk and send the result
        full_summary = ""
        for chunk in chunks:
            summary = summarize_text(chunk)
            full_summary += f"✅ Summary:\n{summary}\n\n"

        await update.message.reply_text(f"📝 Summarized Transcript:\n{full_summary}")
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


