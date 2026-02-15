"""
Twitter Bot for posting AI-generated images based on daily tech news.

This bot fetches the latest US technology news, generates a DALL-E image
related to the news topic, and posts it to Twitter with a summary.
"""

from requests_oauthlib import OAuth1Session
import os
import json
import openai
import requests
import traceback
import tweepy
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Tuple, Set
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MAX_TWEET_LENGTH = 160
MAX_PROMPT_LENGTH = 160
NEWS_COUNTRY = "us"
NEWS_CATEGORY = "technology"
IMAGE_MODEL = "grok-imagine-image-pro"
CHAT_MODEL = "grok-4-1-fast-reasoning"
HISTORY_FILE = Path(__file__).parent / "posted_articles.json"
HISTORY_RETENTION_DAYS = 7

# Load configuration from environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_ENDPOINT = "https://newsapi.org/v2/top-headlines"
XAI_BASE_URL = "https://api.x.ai/v1"

# Validate required environment variables
required_vars = {
    "XAI_API_KEY": XAI_API_KEY,
    "TWITTER_CONSUMER_KEY": CONSUMER_KEY,
    "TWITTER_CONSUMER_SECRET": CONSUMER_SECRET,
    "TWITTER_ACCESS_TOKEN": TWITTER_ACCESS_TOKEN,
    "TWITTER_ACCESS_TOKEN_SECRET": TWITTER_ACCESS_TOKEN_SECRET,
    "NEWS_API_KEY": NEWS_API_KEY,
}

missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please create a .env file based on .env.example and fill in your API keys")
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize xAI client (OpenAI SDK compatible)
client = openai.Client(api_key=XAI_API_KEY, base_url=XAI_BASE_URL)


def load_posted_articles() -> dict:
    """Load posted articles history from JSON file."""
    if not HISTORY_FILE.exists():
        return {}

    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return {}


def save_posted_articles(history: dict) -> None:
    """Save posted articles history to JSON file."""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving history: {e}")


def clean_old_entries(history: dict) -> dict:
    """Remove entries older than HISTORY_RETENTION_DAYS."""
    cutoff = (datetime.now() - timedelta(days=HISTORY_RETENTION_DAYS)).isoformat()
    return {url: timestamp for url, timestamp in history.items() if timestamp > cutoff}


def is_article_posted(url: str, history: dict) -> bool:
    """Check if article URL was recently posted."""
    return url in history


def mark_article_posted(url: str, history: dict) -> dict:
    """Mark article as posted with current timestamp."""
    history[url] = datetime.now().isoformat()
    return history


def fetch_daily_news(api_key: str, history: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Fetches US technology news using NewsAPI, skipping recently posted articles.

    Args:
        api_key: NewsAPI key
        history: Posted articles history

    Returns:
        Tuple of (article_title, article_url, article_description) or (None, None, None) if failed
    """
    params = {
        'country': NEWS_COUNTRY,
        'category': NEWS_CATEGORY,
        'apiKey': api_key
    }

    try:
        response = requests.get(NEWS_API_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()

        articles = response.json().get('articles', [])
        if not articles:
            logger.warning("No articles found in API response")
            return None, None, None

        # Find first unposted article
        for article in articles:
            article_url = article.get('url')
            if not article_url:
                continue

            if not is_article_posted(article_url, history):
                article_description = article.get('description') or article.get('title')
                article_title = article.get('title')
                logger.info(f"Found unposted article: {article_title}")
                return article_title, article_url, article_description

        logger.warning("All articles already posted")
        return None, None, None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news data: {e}")
        return None, None, None


def generate_dalle_prompt(news_description: str) -> Optional[str]:
    """
    Generates image prompt using Grok.

    Args:
        news_description: Description of the news topic

    Returns:
        Generated image prompt or None if failed
    """
    prompt = f"News: '{news_description}'\n\nGenerate hyperrealistic image prompt. Requirements: photographic quality, sharp focus, professional lighting, sharp details. Max {MAX_PROMPT_LENGTH} chars. Output prompt only."

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "Image prompt engineer. Output: dense, photorealistic prompts."},
                {"role": "user", "content": prompt}
            ]
        )
        response_message = response.choices[0].message.content
        logger.info(f"Generated image prompt: {response_message}")
        return response_message

    except Exception as e:
        logger.error(f"Error generating image prompt: {e}")
        return None


def generate_ai_image(prompt: str) -> Optional[str]:
    """
    Generates image using Grok.

    Args:
        prompt: Image generation prompt

    Returns:
        URL of generated image or None if failed
    """
    if not prompt:
        logger.error("Empty prompt")
        return None

    try:
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            n=1
        )

        image_url = response.data[0].url
        logger.info(f"Image URL: {image_url}")
        return image_url

    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None


def generate_tweet_text(news_description: str, news_url: str) -> Optional[str]:
    """
    Generates tweet text using Grok.

    Args:
        news_description: Description of the news topic
        news_url: URL to the news article

    Returns:
        Generated tweet text or None if failed
    """
    prompt = f"News: '{news_description}'\nURL: {news_url}\n\nSummarize as tweet. Include URL when valuable (deals, guides, breaking news, resources). Style: casual journalistic. Tense: past/summary. No CTAs. Max {MAX_TWEET_LENGTH} chars including URL."

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "Tweet writer. Include article URLs for deals, guides, resources, breaking news. Concise, standalone, journalistic."},
                {"role": "user", "content": prompt}
            ]
        )
        response_message = response.choices[0].message.content
        logger.info(f"Tweet text: {response_message}")
        return response_message

    except Exception as e:
        logger.error(f"Tweet generation error: {e}")
        return None


def upload_image_to_twitter(image_url: str, api: tweepy.API) -> Optional[str]:
    """
    Downloads and uploads an image to Twitter.

    Args:
        image_url: URL of the image to upload
        api: Tweepy API instance (v1.1)

    Returns:
        Media ID string or None if failed
    """
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = BytesIO(response.content)

        media = api.media_upload(filename='image.jpg', file=image_data)
        logger.info(f"Successfully uploaded image to Twitter: {media.media_id_string}")
        return media.media_id_string

    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return None


def post_tweet(tweet_text: str, image_url: str, news_title: str, news_url: str) -> None:
    """
    Posts a tweet with an image to Twitter.

    Args:
        tweet_text: Text content of the tweet
        image_url: URL of the image to attach
        news_title: Title of the news article
        news_url: URL of the news article
    """
    # Initialize both v1.1 API and v2 Client
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    twitter_client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    media_id = upload_image_to_twitter(image_url, api)
    if not media_id:
        logger.error("Failed to upload image. Aborting tweet posting.")
        return

    try:
        response = twitter_client.create_tweet(text=tweet_text, media_ids=[media_id])
        logger.info(f"Tweet successfully posted. Response: {response}")

        tweet_id = response.data['id']
        logger.info(f"Tweet ID: {tweet_id}")

    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        traceback.print_exc()


def add_comment_to_tweet(tweet_id: str, news_title: str, news_url: str, client: tweepy.Client) -> None:
    """
    Adds a comment with the source link to a tweet.

    Args:
        tweet_id: ID of the tweet to comment on
        news_title: Title of the news article
        news_url: URL of the news article
        client: Tweepy Client instance
    """
    comment_text = f"[SOURCE]: {news_title} {news_url}"

    try:
        response = client.create_tweet(text=comment_text, in_reply_to_tweet_id=tweet_id)
        logger.info(f"Comment successfully added to tweet. Response: {response}")

    except Exception as e:
        logger.error(f"Error adding comment to tweet: {e}")


def main() -> None:
    """Main bot execution function."""
    logger.info("Starting Twitter bot...")

    try:
        # Load and clean history
        logger.info("Loading posted articles history...")
        history = load_posted_articles()
        history = clean_old_entries(history)
        logger.info(f"Tracking {len(history)} recently posted articles")

        logger.info("Fetching news articles...")
        news_title, news_url, news_description = fetch_daily_news(NEWS_API_KEY, history)

        if not news_url or not news_description:
            logger.error("No unposted articles found")
            return

        logger.info(f"News Title: {news_title}")
        logger.info(f"News Description: {news_description}")
        logger.info(f"News URL: {news_url}")

        logger.info("Generating image prompt...")
        image_prompt = generate_dalle_prompt(news_description)
        if not image_prompt:
            logger.error("Failed to generate image prompt. Aborting.")
            return

        logger.info("Generating image...")
        image_url = generate_ai_image(image_prompt)
        if not image_url:
            logger.error("Failed to generate image. Aborting.")
            return

        logger.info("Generating tweet text...")
        tweet_text = generate_tweet_text(news_description, news_url)
        if not tweet_text:
            logger.error("Failed to generate tweet text. Aborting.")
            return

        logger.info("Posting tweet...")
        post_tweet(tweet_text, image_url, news_title, news_url)

        # Mark article as posted
        history = mark_article_posted(news_url, history)
        save_posted_articles(history)
        logger.info("Article marked as posted")

        logger.info("Bot execution completed successfully!")

    except Exception as e:
        logger.error(f"Error in bot execution: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
