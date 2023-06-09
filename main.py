import os

import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from telegram import InputFile, InputMediaDocument

from tqdm import tqdm

import time

# Telegram bot token

TOKEN = '6174260573:AAHPQe3TgWw8CmAjFXdKtM7rGl6oxmv_Tj4'

# Create an instance of the Updater class

updater = Updater(token=TOKEN, use_context=True)

# Define the handler function for the '/start' command

def start(update, context):

    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the File Downloader Bot!")

# Define the handler function for the '/download' command

def download_file(update, context):

    # Check if a direct download link is provided

    if len(context.args) == 0:

        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a direct download link.")

        return

    download_link = context.args[0]

    file_name = context.args[1] if len(context.args) > 1 else ''

    # Download the file

    context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading file...")

    start_time = time.time()

    response = requests.get(download_link, stream=True)

    total_size = int(response.headers.get('content-length', 0))

    block_size = 1024  # 1KB

    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    downloaded_data = b''

    for data in response.iter_content(block_size):

        progress_bar.update(len(data))

        downloaded_data += data

    progress_bar.close()

    end_time = time.time()

    download_time = end_time - start_time

    download_speed = total_size / download_time / 1024  # in KB/s

    # Rename the file if a new filename is provided

    if file_name:

        file_name = file_name.strip()

        file_extension = os.path.splitext(file_name)[1]

        if not file_extension:

            file_extension = os.path.splitext(download_link)[1]

            file_name += file_extension

    else:

        file_extension = os.path.splitext(download_link)[1]

        file_name = f"downloaded_file{file_extension}"

    # Save the downloaded file

    file_path = f"./{file_name}"

    with open(file_path, 'wb') as file:

        file.write(downloaded_data)

    # Upload the renamed file

    context.bot.send_message(chat_id=update.effective_chat.id, text="Uploading file...")

    send_as_document = context.user_data.get('send_as_document', True)

    if send_as_document:

        start_time = time.time()

        context.bot.send_document(chat_id=update.effective_chat.id, document=InputFile(file_path))

    else:

        start_time = time.time()

        context.bot.send_media_group(chat_id=update.effective_chat.id, media=[InputMediaDocument(InputFile(file_path))])

    end_time = time.time()

    upload_time = end_time - start_time

    upload_speed = total_size / upload_time / 1024  # in KB/s

    # Send the summary

    summary = f"File downloaded and uploaded successfully!\n\nDownload Speed: {download_speed:.2f} KB/s\nUpload Speed: {upload_speed:.2f} KB/s"

    context.bot.send_message(chat_id=update.effective_chat.id, text=summary)

    # Remove the downloaded file

    os.remove(file_path)

# Define the handler function for the '/toggle' command

def toggle_send_mode(update, context):

    send_as_document = not context.user_data.get('send_as_document', True)

    context.user_data['send_as_document'] = send_as_document

    send_mode = "document" if send_as_document else "media"

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Send mode toggled to {send_mode}.")

# Define the handler function for the '/help' command

def help_command(update, context):

    help_text = """

    Available commands:

    /start - Start the bot

    /help - Show help information

    /download <direct_download_link> <filename> - Download a file from a direct download link

    /toggle - Toggle between sending as document or media (album)"""

    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

# Add handlers to the updater

updater.dispatcher.add_handler(CommandHandler('start', start))

updater.dispatcher.add_handler(CommandHandler('download', download_file))

updater.dispatcher.add_handler(CommandHandler('toggle', toggle_send_mode))

updater.dispatcher.add_handler(CommandHandler('help', help_command))

# Start the bot

updater.start_polling()

