"""
Load testing script for URL shortener service.
"""

import random
import string

from locust import HttpUser, between, task


class URLShortenerUser(HttpUser):
    """Load test user for URL shortener."""

    BASE_URL = "/api/v1/link"

    wait_time = between(1, 2)

    def on_start(self):
        """Initialize test data."""
        self.created_urls = []

    @task(1)
    def create_short_url(self):
        """Test creating short URLs."""
        # Generate random URL
        domain = random.choice(["example.com", "test.com", "demo.org"])
        path = "".join(random.choices(string.ascii_lowercase, k=10))
        url = f"https://{domain}/{path}"

        response = self.client.post(
            f"{self.BASE_URL}/shorten", json={"target_url": url}
        )

        if response.status_code == 201:
            data = response.json()
            self.created_urls.append(data.get("shortened_url", ""))

    @task(5)
    def redirect_to_url(self):
        """Test redirecting to original URLs."""
        if not self.created_urls:
            return

        short_url = random.choice(self.created_urls)
        self.client.get(short_url, allow_redirects=False)

    @task(1)
    def get_url_stats(self):
        """Test getting URL statistics."""
        if not self.created_urls:
            return

        short_url = random.choice(self.created_urls)
        self.client.get(f"{self.BASE_URL}/stats/{short_url.split('/')[-1]}")
