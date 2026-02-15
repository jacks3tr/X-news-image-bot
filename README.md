# X Bot - AI-Generated News Images

Automated X bot: fetches US tech news, generates AI images via Grok, posts with AI-generated summaries.

## Features

- 📰 Fetches latest US tech news (NewsAPI)
- 🎨 Generates hyperrealistic images (Grok Imagine Image Pro)
- 🤖 Creates tweet text (Grok-4-1 Fast Reasoning)
- 🐦 Auto-posts to X with images
- 📝 Logging for monitoring/debugging

## Prerequisites

- Python 3.8+
- API Keys:
  - [xAI/Grok API](https://x.ai/api)
  - [X Developer](https://developer.x.com/)
  - [NewsAPI](https://newsapi.org/)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jacks3tr/X-news-image-bot.git
cd X-news-image-bot
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your API credentials:
   ```env
   XAI_API_KEY=your_xai_grok_api_key
   TWITTER_CONSUMER_KEY=your_x_consumer_key
   TWITTER_CONSUMER_SECRET=your_x_consumer_secret
   TWITTER_ACCESS_TOKEN=your_x_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_x_access_token_secret
   NEWS_API_KEY=your_news_api_key
   ```

## Configuration

### X API Setup

1. Create an X Developer Account at [developer.x.com](https://developer.x.com/)
2. Create a new App with **Read and Write** permissions
3. Generate API Keys and Access Tokens
4. Add credentials to your `.env` file

### xAI/Grok API Setup

1. Sign up at [xAI](https://x.ai/)
2. Create API key
3. Add to `.env` file
4. Ensure credits available (Grok Imagine costs apply)

### NewsAPI Setup

1. Register at [NewsAPI.org](https://newsapi.org/)
2. Get your free API key
3. Add to your `.env` file

## Usage

### Running the bot manually

```bash
python Main.py
```

### Running with the scheduler (Windows)

Double-click `Scheduler.bat` or run:

```bash
Scheduler.bat
```

### Scheduling automated runs (Windows Task Scheduler)

1. Open Task Scheduler
2. Create a new task
3. Set the trigger (e.g., daily at 9 AM)
4. Set the action to run `Scheduler.bat`
5. Configure working directory to the project folder

## Testing

Run the test suite:

```bash
python -m pytest test_main.py -v
```

Or with coverage:

```bash
python -m pytest test_main.py -v --cov=Main --cov-report=html
```

## Project Structure

```
X-news-image-bot/
├── .env                    # Your API credentials (DO NOT COMMIT)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore file
├── Main.py                 # Main bot logic
├── test_main.py            # Unit tests
├── requirements.txt        # Python dependencies
├── Scheduler.bat           # Windows batch scheduler
└── README.md               # This file
```

## How It Works

1. **Fetch News**: Retrieves latest US tech news (NewsAPI)
2. **Generate Prompt**: Grok-4-1 creates optimized image prompt from news
3. **Create Image**: Grok Imagine generates hyperrealistic news-related image
4. **Generate Tweet**: Grok-4-1 creates concise tweet summary
5. **Post**: Uploads image, posts to X

## Customization

### Change news category or country

Edit the constants in `Main.py`:

```python
NEWS_COUNTRY = "us"        # Change to any supported country code
NEWS_CATEGORY = "technology"  # Options: business, entertainment, health, science, sports, technology
```

### AI models

```python
IMAGE_MODEL = "grok-imagine-image-pro"
CHAT_MODEL = "grok-4-1-fast-reasoning"
```

## Cost Considerations

- **Grok Imagine Image Pro**: Variable (check xAI pricing)
- **Grok-4-1 Fast Reasoning**: Minimal text generation cost
- **NewsAPI**: Free tier (limited requests/day)
- **X API**: Free tier available

**Estimated cost/run**: ~$0.05 USD (verify current xAI rates)

## Troubleshooting

### Missing environment variables error

Make sure your `.env` file exists and contains all required variables. Check that you've copied `.env.example` to `.env` and filled in your actual API keys.

### X API errors

- Verify your X app has **Read and Write** permissions
- Ensure access tokens are generated with the correct permissions
- Check that you're not rate-limited (X has posting limits)

### xAI/Grok API errors

- Verify API key validity
- Check credits/quota
- Confirm model names correct

### NewsAPI errors

- Free tier has limits (100 requests/day)
- Some articles may not have descriptions
- API requires attribution for free tier usage

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Educational purposes. Comply with:

- [xAI Terms](https://x.ai/legal)
- [X Developer Agreement](https://developer.x.com/en/developer-terms/agreement)
- [NewsAPI Terms](https://newsapi.org/terms)

## Disclaimer

This bot is for educational purposes. Ensure you comply with all applicable terms of service, rate limits, and content policies when using third-party APIs. The authors are not responsible for any misuse or violations.

## Support

For issues, questions, or suggestions:

1. Check existing documentation
2. Review error logs in the console
3. Verify API credentials and quotas
4. Open an issue with detailed information about the problem

---

**Built with:**
- [xAI Grok API](https://x.ai/) - AI image/text generation
- [Tweepy](https://www.tweepy.org/) - X API wrapper
- [NewsAPI](https://newsapi.org/) - News provider
