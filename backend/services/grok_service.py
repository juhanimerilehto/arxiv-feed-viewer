import httpx
import json
import time
import logging
from typing import List, Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class GrokService:
    def __init__(self, api_key: str, model: str = "grok-4-1-fast-reasoning", rate_limit_delay: float = 6.0):
        """
        Initialize Grok xAI service.

        Args:
            api_key: Grok xAI API key
            model: Model name (default: grok-4-1-fast-reasoning)
            rate_limit_delay: Seconds between requests (default 6.0 for 10 req/min)
        """
        self.api_key = api_key
        self.model = model
        self.rate_limit_delay = rate_limit_delay
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True
    )
    async def analyze_paper(
        self,
        title: str,
        abstract: str
    ) -> Optional[List[str]]:
        """
        Analyze a paper using Grok AI to extract key insights.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            List of 5-7 key insight strings (max 120 chars each) or None if failed
        """
        self._rate_limit()

        prompt = f"""You are analyzing an academic paper about GenAI and cybersecurity. Extract 5-7 key technical insights as concise bullet points.

Title: {title}

Abstract: {abstract}

Requirements:
- Each point must be 120 characters or less
- Focus on technical contributions, methods, findings, or implications
- Be specific and actionable
- Avoid generic statements

Return ONLY a JSON array of strings, nothing else. Example format:
["Point 1 here", "Point 2 here", "Point 3 here"]"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a technical research analyst specializing in AI security. Return only valid JSON arrays."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )

                response.raise_for_status()
                data = response.json()

                # Extract content from response
                content = data["choices"][0]["message"]["content"].strip()

                # Parse JSON array
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                key_points = json.loads(content)

                # Validate response
                if not isinstance(key_points, list):
                    logger.error(f"Invalid response format: expected list, got {type(key_points)}")
                    return None

                if not (5 <= len(key_points) <= 7):
                    logger.warning(f"Expected 5-7 points, got {len(key_points)}")

                # Truncate points to 120 chars
                key_points = [point[:120] for point in key_points if isinstance(point, str)]

                logger.info(f"Successfully analyzed paper: {len(key_points)} key points extracted")
                return key_points

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Grok response as JSON: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Grok API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Grok analysis: {e}")
            return None
