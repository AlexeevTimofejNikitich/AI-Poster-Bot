import json
import time
import base64
import os
import requests
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from io import BytesIO
from PIL import Image

# Configuration - replace these with your actual values
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHANNEL_ID = "@YOUR_CHANNEL"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"
FUSION_BRAIN_API_KEY = "YOUR_FUSION_BRAIN_API_KEY"
FUSION_BRAIN_SECRET = "YOUR_FUSION_BRAIN_SECRET"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# List of fairy tale prompts
fairy_tale_prompts = [
    "A magical kingdom where animals can talk",
    "A young hero's quest to find the lost crystal",
    "The adventures of a tiny dragon who couldn't breathe fire",
    "A princess who prefers exploring forests to royal duties",
    "The mystery of the disappearing moon",
    "A group of children who discover a secret portal in their backyard",
    "The kind witch who lived in a candy house",
    "The little robot who wanted to become a real boy",
    "The cloud that refused to rain",
    "The brave mouse who became a knight",
    "The enchanted library where books come to life",
    "The day the colors disappeared from the world",
    "The little star that fell to Earth",
    "The magical paintbrush that made drawings real",
    "The grumpy troll who learned to smile",
    "The secret life of toys when humans aren't looking",
    "The flower that only blooms once every hundred years",
    "The little mermaid who collected human treasures",
    "The wizard who lost his magic but found something better",
    "The kingdom where everyone's shadow had a mind of its own"
]

class FusionBrainAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        """Get the available pipeline ID from FusionBrain API"""
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        """Generate an image based on the prompt"""
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        """Check the status of image generation"""
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']
            attempts -= 1
            time.sleep(delay)

def get_fairy_tale_prompt():
    """Returns a random fairy tale prompt"""
    return f"""Write a magical fairy tale (about 150 words) with the theme: "{random.choice(fairy_tale_prompts)}".
        Requirements:
        1. Wholesome and family-friendly content
        2. Magical elements and adventure
        3. Dynamic storytelling
        4. Can include unusual magical elements
        5. Formatting:
        - Use 5-7 magical emojis like ✨🧙‍♂️🏰🐉🌈 (not in the middle of sentences)
        - Use markdown format
        - Italics for descriptions of feelings
        - **Bold** for key moments
        6. Characters:
        - Can include original characters or known fairy tale characters
        - All ages appropriate

        Don't include "Title:" in the text! Start directly with the content."""

async def generate_text():
    """Generates text using Deepseek API"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": get_fairy_tale_prompt()}
        ],
        "temperature": 0.9,
        "max_tokens": 1000,
        "truncation": "end_sentence",
        "length": 50
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content'].replace("#", "")
        return None
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return None

async def generate_image_prompt(fairy_tale_text):
    """Generates an image prompt based on the fairy tale text"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Create a prompt for generating a cartoon-style image based on this text (10-20 words):
    {fairy_tale_text[:1500]}
    
    The prompt should:
    - Be in English
    - Describe the main scene
    - Specify cartoon style
    - Be concise (under 200 characters)
    - No special characters
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Prompt generation error: {e}")
        return "cartoon style, fairy tale scene, magical atmosphere, bright colors"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    keyboard = [["Generate Content"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Click the button below to generate fairy tale content.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for text messages"""
    if update.message.text == "Generate Content":
        await generate_and_send_content(update, context)

async def generate_and_send_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates and sends content for approval"""
    chat_id = update.effective_chat.id
    
    if str(chat_id) != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ You don't have permission!")
        return
    
    # 1. Generate text
    message = await update.message.reply_text("🔄 Generating fairy tale text...")
    generated_text = await generate_text()
    
    if not generated_text:
        await message.edit_text("❌ Failed to generate text")
        return
    
    # 2. Generate image
    await message.edit_text("🔄 Generating image...")
    try:
        image_prompt = await generate_image_prompt(generated_text)
        api = FusionBrainAPI('https://api-key.fusionbrain.ai/', FUSION_BRAIN_API_KEY, FUSION_BRAIN_SECRET)
        pipeline_id = api.get_pipeline()
        uuid = api.generate(image_prompt, pipeline_id)
        files = api.check_generation(uuid)
        
        if files:
            image_data = base64.b64decode(files[0])
            
            # Save data for possible regeneration
            context.user_data["generated_content"] = {
                "text": generated_text,
                "image_prompt": image_prompt,
                "image_data": image_data,
                "last_message_id": None
            }
            
            # Send content for review
            await send_content_for_review(update, context, generated_text, image_data)
            await message.delete()
            
        else:
            await message.edit_text("❌ Failed to generate image")
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        await message.edit_text(f"❌ Content generation error: {str(e)}")

async def send_content_for_review(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, image_data: bytes):
    """Sends content for review with action buttons"""
    # Create temp file
    temp_image_path = "temp_image.jpg"
    with open(temp_image_path, "wb") as img_file:
        img_file.write(image_data)
    
    # Send photo with text
    with open(temp_image_path, "rb") as photo:
        sent_message = await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo,
            caption=text[:1024],
            parse_mode="Markdown"
        )
    
    # Save message ID for possible deletion
    context.user_data["generated_content"]["last_message_id"] = sent_message.message_id
    os.remove(temp_image_path)
    
    # Action buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Publish", callback_data='publish'),
            InlineKeyboardButton("🔄 Regenerate Image", callback_data='regenerate_image')
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text="Choose an action:",
        reply_markup=reply_markup
    )

async def regenerate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Regenerates image for existing text"""
    query = update.callback_query
    await query.answer()
    
    content = context.user_data.get("generated_content")
    if not content:
        await query.edit_message_text("❌ No data to regenerate")
        return
    
    # Delete previous image message
    if content.get("last_message_id"):
        try:
            await context.bot.delete_message(
                chat_id=ADMIN_CHAT_ID,
                message_id=content["last_message_id"]
            )
        except Exception as e:
            logger.error(f"Message deletion error: {e}")
    
    # Generate new image
    await query.edit_message_text("🔄 Regenerating image...")
    try:
        api = FusionBrainAPI('https://api-key.fusionbrain.ai/', FUSION_BRAIN_API_KEY, FUSION_BRAIN_SECRET)
        pipeline_id = api.get_pipeline()
        uuid = api.generate(content["image_prompt"], pipeline_id)
        files = api.check_generation(uuid)
        
        if files:
            new_image_data = base64.b64decode(files[0])
            context.user_data["generated_content"]["image_data"] = new_image_data
            
            # Send updated content
            await send_content_for_review(update, context, content["text"], new_image_data)
            await query.delete()
        else:
            await query.edit_message_text("❌ Failed to regenerate image")
    except Exception as e:
        logger.error(f"Image regeneration error: {str(e)}")

async def publish_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Publishes content to channel"""
    query = update.callback_query
    content = context.user_data.get("generated_content")
    
    if content:
        try:
            temp_path = "to_publish.jpg"
            with open(temp_path, "wb") as f:
                f.write(content["image_data"])
            
            with open(temp_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=content["text"][:1024],
                    parse_mode="Markdown"
                )
            
            os.remove(temp_path)
            await query.edit_message_text("✅ Content published in channel!")
            context.user_data.pop("generated_content", None)
        except Exception as e:
            await query.edit_message_text(f"❌ Publication error: {str(e)}")
    else:
        await query.edit_message_text("❌ No data to publish")

async def cancel_publication(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels publication"""
    query = update.callback_query
    await query.edit_message_text("❌ Publication canceled")
    context.user_data.pop("generated_content", None)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'publish':
        await publish_content(update, context)
    elif query.data == 'regenerate_image':
        await regenerate_image(update, context)
    elif query.data == 'cancel':
        await cancel_publication(update, context)

async def post_init(application: Application):
    """Post-initialization"""
    logger.info("Bot started")
    await application.bot.delete_webhook()
    await application.bot.get_updates(offset=-1)

def main():
    """Starts the bot"""
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Starting bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()