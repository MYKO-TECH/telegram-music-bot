# -*- coding: utf-8 -*-
"""
A Telegram bot that finds YouTube Music links for songs.
"""

import logging
import os  # <-- Import the 'os' module
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from youtubesearchpython import VideosSearch

# --- Configuration ---
# We will get the token from an environment variable on Render.
# This is much more secure than writing the token directly in the code.
TELEGRAM_BOT_TOKEN = os.environ.get('8349723451:AAG7t25qLjMVSc8jCiSUgKYnozkRW3oSOY8')

# Enable logging to see errors and bot activity in your console.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the user sends the /start command."""
    user = update.effective_user
    welcome_message = (
        f"Hi {user.mention_html()}! 👋\n\n"
        "I'm your personal YouTube Music finder.\n\n"
        "Just send me the name of any song, and I'll send you the YouTube Music link for it. "
        "For example, try sending: 'Bohemian Rhapsody'"
    )
    await update.message.reply_html(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the user sends the /help command."""
    help_text = (
        "<b>How to use me:</b>\n\n"
        "1. Simply type the name of the song you want to find.\n"
        "2. You can also include the artist for more accurate results (e.g., 'Queen - Another One Bites the Dust').\n"
        "3. I will search YouTube and give you the first result as a YouTube Music link.\n\n"
        "That's it! Happy listening. 🎶"
    )
    await update.message.reply_html(help_text)


# --- Core Logic ---

async def find_music_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles regular text messages, searches for the song, and returns a YouTube Music link.
    """
    song_query = update.message.text
    logger.info(f"Received song query from user {update.effective_user.id}: '{song_query}'")

    await update.message.reply_text(f"Searching for '{song_query}'...")

    try:
        search = VideosSearch(song_query, limit=1)
        search_results = search.result()

        if not search_results or not search_results.get('result'):
            await update.message.reply_text(
                "Sorry, I couldn't find a matching song. 😔\n"
                "Please check the spelling or try a different name."
            )
            return

        top_result = search_results['result'][0]
        video_id = top_result['id']
        video_title = top_result['title']
        video_duration = top_result['duration']
        music_url = f"https://music.youtube.com/watch?v={video_id}"

        response_message = (
            f"✅ Found it!\n\n"
            f"<b>🎵 Title:</b> {video_title}\n"
            f"<b>⏳ Duration:</b> {video_duration}\n\n"
            f"<b>🔗 Your Link:</b> <a href='{music_url}'>Listen on YouTube Music</a>"
        )

        await update.message.reply_html(response_message, disable_web_page_preview=False)
        logger.info(f"Sent link for '{video_title}' to user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"An error occurred while searching for '{song_query}': {e}", exc_info=True)
        await update.message.reply_text(
            "An unexpected error occurred. Please try again in a moment."
        )


# --- Main Bot Setup ---

def main() -> None:
    """Sets up the bot, adds handlers, and starts polling for updates."""
    # Check if the token was loaded correctly from the environment variable.
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: The TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
        
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, find_music_link))

    print("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()
