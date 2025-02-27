import openai
from llama_index import VectorStoreIndex
from llama_index.schema import Document
import yt_dlp as youtube_dl  # Using yt-dlp instead of youtube_dl

import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Function to download the YouTube video transcript
def download_youtube_transcript(url):
    ydl_opts = {
        'quiet': True,
        'writeinfojson': True,
        'extractaudio': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        transcript = info_dict.get('description', '')
        return transcript

# Function to summarize using OpenAI API
def summarize_text(text):
    response = openai.ChatCompletion.create(
        api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize this text: {text}"}],
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()


# Function to store and index the summary with LlamaIndex
def index_summary(summary):
    doc = Document(text=summary)
    index = VectorStoreIndex.from_documents([doc])
    return index

# Main function
def main(youtube_url):
    transcript = download_youtube_transcript(youtube_url)
    print("Transcript downloaded successfully!")

    if transcript:
        print("Summarizing...")
        summary = summarize_text(transcript)
        print("Summary:", summary)

        print("Indexing summary with LlamaIndex...")
        index = index_summary(summary)
        print("Indexing complete!")

    else:
        print("Could not retrieve transcript for the video.")

if __name__ == "__main__":
    youtube_url = input("Enter the YouTube video URL: ")
    main(youtube_url)




