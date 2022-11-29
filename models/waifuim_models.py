"""
Models for waifu and nsfw module
"""

from datetime import datetime

class Image:
    """
    Image class
    """

    def __init__(self, image_data) -> None:

        self.signature: str = image_data["signature"]
        self.extension: str = image_data["extension"]
        self.image_id = int(image_data["image_id"])
        self.dominant_color: str = image_data["dominant_color"]
        self.source: str = image_data["source"]
        self.uploaded_at = datetime.fromisoformat(image_data["uploaded_at"])
        self.is_nsfw: str = image_data["is_nsfw"]
        self.width = int(image_data["width"])
        self.height = int(image_data["height"])
        self.url: str = image_data["url"]
        self.preview_url: str = image_data["preview_url"]
        self.tags = [tag for tag in image_data["tags"]]
