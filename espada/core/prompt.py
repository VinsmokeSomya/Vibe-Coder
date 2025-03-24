import json  # Importing json module for handling JSON operations

from typing import Dict, Optional  # Importing Dict and Optional types for type hinting

class Prompt:
    def __init__(
        self,
        text: str,
        image_urls: Optional[Dict[str, str]] = None,
        entrypoint_prompt: str = "",
    ):
        # Initialize the Prompt object with text, optional image URLs, and an entrypoint prompt
        self.text = text
        self.image_urls = image_urls
        self.entrypoint_prompt = entrypoint_prompt

    def __repr__(self):
        # Return a string representation of the Prompt object for debugging
        return f"Prompt(text={self.text!r}, image_urls={self.image_urls!r})"

    def to_langchain_content(self):
        # Convert the Prompt object to a format compatible with Langchain content
        content = [{"type": "text", "text": f"Request: {self.text}"}]

        if self.image_urls:
            # If there are image URLs, add them to the content with low detail
            for name, url in self.image_urls.items():
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                        "detail": "low",
                    },
                }
                content.append(image_content)

        return content

    def to_dict(self):
        # Convert the Prompt object to a dictionary representation
        return {
            "text": self.text,
            "image_urls": self.image_urls,
            "entrypoint_prompt": self.entrypoint_prompt,
        }

    def to_json(self):
        # Convert the Prompt object to a JSON string
        return json.dumps(self.to_dict())
