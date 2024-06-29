import telebot
from pytube import YouTube
import os

bot = telebot.TeleBot('7390359895:AAH8TrulQh9Ws3GSyamfM-HNQcrJQ5aTSg4')

# Global variables to hold the chat id and last sent message id for progress updates
current_chat_id = None
last_message_id = None

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a YouTube video link to download.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_chat_id, last_message_id
    try:
        url = message.text
        if not YouTube(url).check_availability() is None:
            bot.reply_to(message, "Please send a valid YouTube link.")
            return

        yt = YouTube(url, on_progress_callback=on_progress)

        # Show video information
        video_info = f"Title: {yt.title}\nLength: {yt.length // 60} minutes {yt.length % 60} seconds\nViews: {yt.views}"
        bot.reply_to(message, video_info)

        stream = yt.streams.filter(
            progressive=True,
            file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            # Set the current chat id for progress updates
            current_chat_id = message.chat.id
            last_message_id = None  # Reset last message id for new download

            # Download the video
            bot.reply_to(message, f"Downloading \"{yt.title}\"...")
            file_path = stream.download()

            # Check the file size
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                bot.reply_to(
                    message,
                    "Sorry, the video is too large to be sent via Telegram.")
                os.remove(file_path)  # Cleanup the large file
                return

            # Send the downloaded file
            video_file = open(file_path, 'rb')
            bot.send_video(message.chat.id, video_file, caption=yt.title)

            # Cleanup: Delete the downloaded file from the server
            video_file.close()
            os.remove(file_path)

            bot.reply_to(message, "Video sent successfully!")
        else:
            bot.reply_to(message, "Sorry, couldn't find a downloadable video.")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")


def on_progress(stream, chunk, bytes_remaining):
    global last_message_id
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = int(bytes_downloaded / total_size * 100)

    # Create a text-based progress bar
    bar_length = 20
    filled_length = int(bar_length * percentage_of_completion / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    progress_message = f"Downloading: [{bar}] {percentage_of_completion}% complete"

    if last_message_id:
        bot.edit_message_text(progress_message, current_chat_id,
                              last_message_id)
    else:
        sent_message = bot.send_message(current_chat_id, progress_message)
        last_message_id = sent_message.message_id


if __name__ == "__main__":
    bot.polling()
