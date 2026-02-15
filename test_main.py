"""Unit tests for the Twitter bot."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import Main


class TestBot(unittest.TestCase):
    """Test suite for Twitter bot functionality."""

    @patch('Main.requests.get')
    def test_fetch_daily_news_success(self, mock_get):
        """Test successful news fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [{
                'title': 'News Title',
                'url': 'https://news.com',
                'description': 'News Description'
            }]
        }
        mock_get.return_value = mock_response

        title, url, description = Main.fetch_daily_news("fake_api_key", {})

        self.assertEqual(title, "News Title")
        self.assertEqual(url, "https://news.com")
        self.assertEqual(description, "News Description")

    @patch('Main.requests.get')
    def test_fetch_daily_news_skip_posted(self, mock_get):
        """Test news fetch skips already posted articles."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {'title': 'Old News', 'url': 'https://old.com', 'description': 'Old'},
                {'title': 'New News', 'url': 'https://new.com', 'description': 'New'}
            ]
        }
        mock_get.return_value = mock_response

        history = {'https://old.com': '2024-01-01T00:00:00'}
        title, url, description = Main.fetch_daily_news("fake_api_key", history)

        self.assertEqual(title, "New News")
        self.assertEqual(url, "https://new.com")

    @patch('Main.requests.get')
    def test_fetch_daily_news_no_articles(self, mock_get):
        """Test news fetch with no articles."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'articles': []}
        mock_get.return_value = mock_response

        title, url, description = Main.fetch_daily_news("fake_api_key", {})

        self.assertIsNone(title)
        self.assertIsNone(url)
        self.assertIsNone(description)

    @patch('Main.client.chat.completions.create')
    def test_generate_dalle_prompt(self, mock_create):
        """Test image prompt generation."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Generated image prompt"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        prompt = Main.generate_dalle_prompt("News Description")

        self.assertEqual(prompt, "Generated image prompt")
        mock_create.assert_called_once()

    @patch('Main.client.images.generate')
    def test_generate_ai_image(self, mock_generate):
        """Test image generation."""
        mock_data = MagicMock()
        mock_data.url = "https://generated-image.com"
        mock_response = MagicMock()
        mock_response.data = [mock_data]
        mock_generate.return_value = mock_response

        image_url = Main.generate_ai_image("Image prompt")

        self.assertEqual(image_url, "https://generated-image.com")
        mock_generate.assert_called_once()

    def test_generate_ai_image_empty_prompt(self):
        """Test image generation with empty prompt."""
        image_url = Main.generate_ai_image("")

        self.assertIsNone(image_url)

    @patch('Main.client.chat.completions.create')
    def test_generate_tweet_text(self, mock_create):
        """Test tweet text generation."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Generated tweet text"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        tweet_text = Main.generate_tweet_text("News Description", "https://news.com")

        self.assertEqual(tweet_text, "Generated tweet text")
        mock_create.assert_called_once()

    @patch('Main.requests.get')
    def test_upload_image_to_twitter(self, mock_get):
        """Test image upload to Twitter."""
        mock_api = MagicMock()
        mock_media = MagicMock()
        mock_media.media_id_string = "123456789"
        mock_api.media_upload.return_value = mock_media

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        media_id = Main.upload_image_to_twitter("https://image.com", mock_api)

        self.assertEqual(media_id, "123456789")

    def test_is_article_posted(self):
        """Test article posted check."""
        history = {'https://example.com': '2024-01-01T00:00:00'}

        self.assertTrue(Main.is_article_posted('https://example.com', history))
        self.assertFalse(Main.is_article_posted('https://new.com', history))

    def test_mark_article_posted(self):
        """Test marking article as posted."""
        history = {}
        history = Main.mark_article_posted('https://example.com', history)

        self.assertIn('https://example.com', history)

    def test_clean_old_entries(self):
        """Test cleaning old history entries."""
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        recent_date = datetime.now().isoformat()

        history = {
            'https://old.com': old_date,
            'https://recent.com': recent_date
        }

        cleaned = Main.clean_old_entries(history)

        self.assertNotIn('https://old.com', cleaned)
        self.assertIn('https://recent.com', cleaned)


if __name__ == '__main__':
    unittest.main()
