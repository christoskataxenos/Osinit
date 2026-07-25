import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any

import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Ρύθμιση καταγραφής συμβάντων (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("telegram_osint_bot")

# Μεταβλητές περιβάλλοντος για το Token του Bot και το API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = os.getenv("API_URL", "http://api:8000/api/v1/incidents")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Χειριστής της εντολής /start.
    Καλωσορίζει τον χρήστη και εξηγεί τη λειτουργία υποβολής αναφορών OSINT.
    """
    if not update.message:
        return

    welcome_message = (
        "🛰️ **OSINT Conflict Reporting Bot**\n\n"
        "Καλώς ήρθατε στο σύστημα συλλογής πληροφοριών ένοπλων σύγκρουσεων.\n\n"
        "**Πώς να υποβάλετε αναφορά:**\n"
        "Στείλτε ένα μήνυμα με την πληροφορία ή την είδηση που θέλετε να καταχωρηθεί.\n"
        "• Η πρώτη γραμμή θα χρησιμοποιηθεί ως **Τίτλος**.\n"
        "• Το υπόλοιπο κείμενο θα καταχωρηθεί ως **Περιγραφή**.\n\n"
        "Επίσης, μπορείτε να προσθέσετε αυτό το Bot ως Διαχειριστή (Admin) σε κανάλια Telegram για αυτόματη λήψη αναρτήσεων!\n\n"
        "Χρησιμοποιήστε την εντολή /help για περισσότερες λεπτομέρειες."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Χειριστής της εντολής /help.
    Παρέχει οδηγίες για τη μορφή των αναφορών.
    """
    if not update.message:
        return

    help_text = (
        "ℹ️ **Οδηγίες Χρήσης Bot**\n\n"
        "1. Στείλτε οποιοδήποτε κείμενο/είδηση για ένοπλες συρράξεις.\n"
        "2. Προσθέστε το Bot ως **Admin** σε δημόσια/ιδιωτικά κανάλια για αυτόματη σάρωση ειδήσεων.\n"
        "3. Όλα τα περιστατικά στέλνονται αυτόματα στο τοπικό OSINT API και εμφανίζονται στο React Dashboard (`http://localhost:3000`)."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_incoming_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Χειριστής εισερχόμενων μηνυμάτων κειμένου από προσωπικές συνομιλίες ή ομάδες.
    """
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    user = update.message.from_user
    username = user.username if user and user.username else f"User_{user.id if user else 'Unknown'}"

    # Διαχωρισμός πρώτης γραμμής για τίτλο και υπόλοιπου κειμένου για περιγραφή
    lines = user_text.split("\n", 1)
    title = lines[0][:255]
    description = lines[1].strip() if len(lines) > 1 else user_text

    incident_payload: Dict[str, Any] = {
        "title": f"[Telegram Report] {title}",
        "description": f"{description}\n\nSubmitted by Telegram User: @{username}",
        "source_name": f"Telegram (@{username})",
        "source_url": f"https://t.me/{username}",
        "is_darknet": False,
        "date_reported": datetime.now(timezone.utc).isoformat()
    }

    logger.info(f"Αποστολή αναφοράς από χρήστη Telegram @{username} στο API...")

    try:
        response = requests.post(API_URL, json=incident_payload, timeout=10)
        if response.status_code in [200, 201]:
            created_id = response.json().get("id", "Unknown")
            reply_msg = (
                f"✅ **Η αναφορά καταχωρήθηκε επιτυχώς!**\n\n"
                f"🆔 **UUID:** `{created_id}`\n"
                f"📌 **Τίτλος:** {title}\n\n"
                f"Μπορείτε να τη δείτε στο OSINT Dashboard."
            )
            await update.message.reply_text(reply_msg, parse_mode="Markdown")
        else:
            logger.error(f"Σφάλμα API HTTP {response.status_code}: {response.text}")
            await update.message.reply_text("❌ Σφάλμα κατά την καταχώρηση στη βάση δεδομένων.")

    except Exception as err:
        logger.error(f"Αποτυχία επικοινωνίας με το API: {err}")
        await update.message.reply_text("⚠️ Αποτυχία σύνδεσης με το τοπικό OSINT API.")


async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Χειριστής αυτόματων αναρτήσεων από Telegram Channels στα οποία είναι μέλος/Admin το Bot.
    """
    post = update.channel_post or update.edited_channel_post
    if not post:
        return

    text = post.text or post.caption
    if not text:
        return

    chat_title = post.chat.title or "Telegram Channel"
    chat_username = post.chat.username

    source_name = f"Telegram Channel ({chat_title})"
    if chat_username:
        source_url = f"https://t.me/{chat_username}/{post.message_id}"
    else:
        clean_chat_id = str(post.chat.id).replace("-100", "")
        source_url = f"https://t.me/c/{clean_chat_id}/{post.message_id}"

    lines = text.strip().split("\n", 1)
    title = lines[0][:255]
    description = lines[1].strip() if len(lines) > 1 else text

    incident_payload: Dict[str, Any] = {
        "title": f"[{chat_title}] {title}",
        "description": description,
        "source_name": source_name,
        "source_url": source_url,
        "is_darknet": False,
        "date_reported": post.date.isoformat() if post.date else datetime.now(timezone.utc).isoformat()
    }

    logger.info(f"Αυτόματη λήψη ανάρτησης από Telegram Channel '{chat_title}' (Msg ID: {post.message_id})...")

    try:
        response = requests.post(API_URL, json=incident_payload, timeout=10)
        if response.status_code in [200, 201]:
            created_id = response.json().get("id", "Unknown")
            logger.info(f"Επιτυχής καταχώρηση ανάρτησης καναλιού στο API! UUID: {created_id}")
        else:
            logger.error(f"Σφάλμα API κατά την καταχώρηση ανάρτησης καναλιού HTTP {response.status_code}: {response.text}")
    except Exception as err:
        logger.error(f"Αποτυχία αποστολής ανάρτησης καναλιού στο API: {err}")


def main() -> None:
    """
    Κύρια συνάρτηση εκκίνησης του Telegram Bot.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Δεν βρέθηκε TELEGRAM_BOT_TOKEN στις μεταβλητές περιβάλλοντος!")
        return

    logger.info("Εκκίνηση Telegram OSINT Collector Bot...")

    # Δημιουργία εφαρμογής Telegram Bot
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Εγγραφή handlers εντολών, μηνυμάτων και αναρτήσεων καναλιών
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Χειριστής αναρτήσεων από Telegram Channels
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    
    # Χειριστής προσωπικών μηνυμάτων / ομάδων
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message))

    # Έναρξη polling μηνυμάτων
    application.run_polling()


if __name__ == "__main__":
    main()
