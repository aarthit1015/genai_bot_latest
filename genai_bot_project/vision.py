from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
from typing import Tuple, List
from utils import setup_logger
import torch

logger = setup_logger(__name__)

class VisionCaptioner:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base", device=None):
        # Automatically select GPU if available, otherwise CPU
        self.device = device if device is not None else ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        logger.info(f"Loaded BLIP model on {self.device}")

    def caption_from_bytes(self, img_bytes: bytes) -> Tuple[str, List[str]]:
        try:
            # Read image from Telegram upload
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            # Preprocess the image
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)

            #  Correct way — generate caption directly from pixel_values
            out = self.model.generate(**inputs, max_new_tokens=50)

            # Decode caption
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            # Extract simple tags
            tags = self._extract_tags(caption)
            return caption, tags

        except Exception as e:
            logger.error(f"Vision model error: {e}")
            return "❌ Failed to generate caption.", ["error"]

    def _extract_tags(self, caption: str):
        # Very simple keyword picker (first 3 unique words)
        words = [w.strip(".,!?()").lower() for w in caption.split() if len(w) > 2]
        seen = []
        for w in words:
            if w not in seen:
                seen.append(w)
            if len(seen) >= 3:
                break
        return seen
