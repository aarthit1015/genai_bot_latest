# telegram_bot.py
import os
import time
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from utils import setup_logger
from rag import MiniRAG
from vision import VisionCaptioner
from db import init_db, add_history, get_history
import logging
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


logger = setup_logger("telegram_bot")

# TOKEN = os.environ.get("TELEGRAM_TOKEN")
TOKEN = "BOT TOKEN"
if not TOKEN:
    logger.error("Set TELEGRAM_TOKEN environment variable")
    raise SystemExit("TELEGRAM_TOKEN not set")

# initialize systems
rag = MiniRAG()
vision = VisionCaptioner()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am GenAI bot. Use /ask <query>, /image, /help")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *GenAI Helper Bot — Commands Guide*\n\n"
        "Select what you’d like to do 👇\n\n"
        "/ask `<your question>` — Ask from stored documents\n"
        "/image — Upload an image for AI captioning\n"
        "/help — Show this help message again\n\n"
        "💡 Example:\n"
        "`/ask What is the leave policy?`\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("🧠 Ask a Question", switch_inline_query_current_chat="/ask "),
            InlineKeyboardButton("🖼️ Upload Image", switch_inline_query_current_chat="/image"),
        ],
        [InlineKeyboardButton("ℹ️ Help", switch_inline_query_current_chat="/help")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=reply_markup)


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /ask <query>")
        return
    ts = int(time.time())
    add_history(user_id, ts, "user", query)
    await update.message.chat.send_action("typing")
    answer = rag.answer(query)
    add_history(user_id, ts+1, "bot", answer)
    await update.message.reply_text(answer)

# /image flow: user sends /image then attaches an image; simplest approach: accept images anytime and process
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    user_id = str(user.id)
    if not msg.photo:
        await msg.reply_text("Please attach an image (photo).")
        return
    # get highest resolution
    file = await msg.photo[-1].get_file()
    img_bytes = await file.download_as_bytearray()
    await msg.chat.send_action("upload_photo")
    caption, tags = vision.caption_from_bytes(bytes(img_bytes))
    ts = int(time.time())
    add_history(user_id, ts, "user", "[image uploaded]")
    add_history(user_id, ts+1, "bot", caption)
    text = f"Caption: {caption}\nTags: {', '.join(tags)}"
    await msg.reply_text(text)

async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    hist = get_history(user_id, limit=10)
    if not hist:
        await update.message.reply_text("No recent history.")
        return
    # join last texts concisely and ask generator for summary
    texts = "\n".join([f"{role}: {text}" for role, text in hist])
    summary = rag.generator(f"Summarize briefly:\n\n{texts}", max_length=100)[0]["generated_text"]
    await update.message.reply_text("Summary:\n" + summary)
    



def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("summarize", summarize_cmd))
    # image message handler
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))
    logger.info("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()

