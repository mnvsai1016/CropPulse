"""Root-level alias forwarding to agri_guide.utils.crop_manager."""
from agri_guide.utils.crop_manager import (
    CropManager,
    RECOMMENDATION_CROPS,
    FERTILIZER_CROP_CLASSES,
    YIELD_DISPLAY_OVERRIDES,
    YIELD_CROP_CLASSES,
)

__all__ = [
    "CropManager",
    "RECOMMENDATION_CROPS",
    "FERTILIZER_CROP_CLASSES",
    "YIELD_DISPLAY_OVERRIDES",
    "YIELD_CROP_CLASSES",
]
