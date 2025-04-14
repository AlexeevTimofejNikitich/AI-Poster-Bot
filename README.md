# Fairy Tale Generator Telegram Bot 🤖✨

A Telegram bot that generates magical fairy tales with accompanying cartoon-style illustrations. Perfect for creating wholesome, family-friendly content for channels or personal enjoyment.

## Features 🌟

- **AI-Generated Fairy Tales**: Creates unique magical stories using Deepseek's language model
- **Cartoon Illustrations**: Generates matching images in cartoon style via FusionBrain API
- **Admin Approval System**: Content is first sent to admin for review before publishing
- **Interactive Interface**: Simple buttons for generating and managing content
- **Markdown Formatting**: Stories include emojis and formatting for better readability

## How It Works ⚙️

1. Admin requests new content via "/start" or "Generate Content" button
2. Bot generates:
   - A fairy tale story (150 words) using Deepseek API
   - A cartoon-style illustration based on the story using FusionBrain API
3. Content is sent to admin for approval
4. Admin can:
   - Publish to channel
   - Regenerate the image
   - Cancel publication

## Setup Instructions 🛠️

### Prerequisites

- Python 3.8+
- Telegram bot token
- Deepseek API key
- FusionBrain API key and secret
- Telegram channel for publishing (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fairy-tale-bot.git
   cd fairy-tale-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```env
   TOKEN=your_telegram_bot_token
   CHANNEL_ID=@your_channel
   ADMIN_CHAT_ID=your_admin_chat_id
   DEEPSEEK_API_KEY=your_deepseek_key
   FUSION_BRAIN_API_KEY=your_fusionbrain_key
   FUSION_BRAIN_SECRET=your_fusionbrain_secret
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Configuration ⚙️

You can customize these aspects:

- **Story Prompts**: Modify `fairy_tale_prompts` list in `bot.py`
- **Story Length**: Adjust `max_tokens` in `generate_text()`
- **Image Style**: Change the default prompt in `generate_image_prompt()`
- **Image Size**: Modify `width` and `height` in `generate()` method

## Usage Guide 

### For Admins

1. Start the bot with `/start`
2. Click "Generate Content"
3. Review the generated story and image
4. Choose to:
   - ✅ Publish - Shares to your channel
   - 🔄 Regenerate Image - Creates new illustration
   - ❌ Cancel - Discards the content

### For Channel Subscribers

The published content will appear in your connected Telegram channel with:
- The generated fairy tale story
- Matching cartoon-style illustration

## API Documentation 🔗

This bot uses two external APIs:

1. **Deepseek API**:
   - Used for text generation
   - [Deepseek Documentation](https://deepseek.com/docs)

2. **FusionBrain API**:
   - Used for image generation
   - [FusionBrain Documentation](https://fusionbrain.ai/docs)

## Project Structure 📂

```
fairy-tale-bot/
├── bot.py                # Main bot application
├── README.md             # This documentation
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (ignored in git)
```

## Contributing 🤝

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

✨ Happy storytelling! May your channel be filled with magical adventures! ✨
```
