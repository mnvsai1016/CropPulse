"""Unified Crop Manager for CropPulse.

Harmonizes and manages crop taxonomy across all 3 Machine Learning modules:
1. Module 1: Crop Recommendation (22 target crops)
2. Module 2: Yield Prediction (124 crop production classes)
3. Module 3: Soil Health & Fertilizer Recommendation (11 crop categories)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any


# -----------------------------------------------------------------------------
# 1. Module 1: Crop Recommendation Target Crops (22 Classes)
# -----------------------------------------------------------------------------
RECOMMENDATION_CROPS: Dict[str, Dict[str, Any]] = {
    "rice": {
        "canonical_id": "rice",
        "display_name": "Rice (Paddy)",
        "emoji": "🌾",
        "category": "Cereals",
        "yield_class": "Rice",
        "fertilizer_class": "Paddy",
        "aliases": ["rice", "paddy", "chawal", "dhan", "rice (paddy)"]
    },
    "maize": {
        "canonical_id": "maize",
        "display_name": "Maize (Corn)",
        "emoji": "🌽",
        "category": "Cereals",
        "yield_class": "Maize",
        "fertilizer_class": "Maize",
        "aliases": ["maize", "corn", "makka", "makai", "maize (corn)"]
    },
    "chickpea": {
        "canonical_id": "chickpea",
        "display_name": "Chickpea (Gram)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Gram",
        "fertilizer_class": "Pulses",
        "aliases": ["chickpea", "chickpeas", "gram", "chana", "bengal gram", "chickpea (gram)"]
    },
    "kidneybeans": {
        "canonical_id": "kidneybeans",
        "display_name": "Kidney Beans (Rajma)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Rajmash Kholar",
        "fertilizer_class": "Pulses",
        "aliases": ["kidneybeans", "kidney beans", "rajma", "rajmash", "rajmash kholar", "bean"]
    },
    "pigeonpeas": {
        "canonical_id": "pigeonpeas",
        "display_name": "Pigeon Peas (Arhar/Tur)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Arhar/Tur",
        "fertilizer_class": "Pulses",
        "aliases": ["pigeonpeas", "pigeon peas", "arhar", "tur", "toor", "arhar/tur", "red gram"]
    },
    "mothbeans": {
        "canonical_id": "mothbeans",
        "display_name": "Moth Beans",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Moth",
        "fertilizer_class": "Pulses",
        "aliases": ["mothbeans", "moth beans", "moth", "matki"]
    },
    "mungbean": {
        "canonical_id": "mungbean",
        "display_name": "Mung Bean (Moong)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Moong(Green Gram)",
        "fertilizer_class": "Pulses",
        "aliases": ["mungbean", "mung bean", "moong", "green gram", "moong(green gram)"]
    },
    "blackgram": {
        "canonical_id": "blackgram",
        "display_name": "Blackgram (Urad)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Blackgram",
        "fertilizer_class": "Pulses",
        "aliases": ["blackgram", "black gram", "urad", "urad dal"]
    },
    "lentil": {
        "canonical_id": "lentil",
        "display_name": "Lentil (Masoor)",
        "emoji": "🫘",
        "category": "Pulses",
        "yield_class": "Lentil",
        "fertilizer_class": "Pulses",
        "aliases": ["lentil", "lentils", "masoor", "masoor dal"]
    },
    "pomegranate": {
        "canonical_id": "pomegranate",
        "display_name": "Pomegranate",
        "emoji": "🍎",
        "category": "Fruits",
        "yield_class": "Pome Granet",
        "fertilizer_class": "Pulses",
        "aliases": ["pomegranate", "pome granet", "anar"]
    },
    "banana": {
        "canonical_id": "banana",
        "display_name": "Banana",
        "emoji": "🍌",
        "category": "Fruits",
        "yield_class": "Banana",
        "fertilizer_class": "Pulses",
        "aliases": ["banana", "kela"]
    },
    "mango": {
        "canonical_id": "mango",
        "display_name": "Mango",
        "emoji": "🥭",
        "category": "Fruits",
        "yield_class": "Mango",
        "fertilizer_class": "Pulses",
        "aliases": ["mango", "aam"]
    },
    "grapes": {
        "canonical_id": "grapes",
        "display_name": "Grapes",
        "emoji": "🍇",
        "category": "Fruits",
        "yield_class": "Grapes",
        "fertilizer_class": "Pulses",
        "aliases": ["grapes", "angoor"]
    },
    "watermelon": {
        "canonical_id": "watermelon",
        "display_name": "Watermelon",
        "emoji": "🍉",
        "category": "Fruits",
        "yield_class": "Water Melon",
        "fertilizer_class": "Pulses",
        "aliases": ["watermelon", "water melon", "tarbooz"]
    },
    "muskmelon": {
        "canonical_id": "muskmelon",
        "display_name": "Muskmelon",
        "emoji": "🍈",
        "category": "Fruits",
        "yield_class": "Water Melon",
        "fertilizer_class": "Pulses",
        "aliases": ["muskmelon", "kharbooja", "cantaloupe", "melon"]
    },
    "apple": {
        "canonical_id": "apple",
        "display_name": "Apple",
        "emoji": "🍎",
        "category": "Fruits",
        "yield_class": "Apple",
        "fertilizer_class": "Pulses",
        "aliases": ["apple", "seb"]
    },
    "orange": {
        "canonical_id": "orange",
        "display_name": "Orange",
        "emoji": "🍊",
        "category": "Fruits",
        "yield_class": "Orange",
        "fertilizer_class": "Pulses",
        "aliases": ["orange", "santra", "narangi"]
    },
    "papaya": {
        "canonical_id": "papaya",
        "display_name": "Papaya",
        "emoji": "🥭",
        "category": "Fruits",
        "yield_class": "Papaya",
        "fertilizer_class": "Pulses",
        "aliases": ["papaya", "papita"]
    },
    "coconut": {
        "canonical_id": "coconut",
        "display_name": "Coconut",
        "emoji": "🥥",
        "category": "Plantation",
        "yield_class": "Coconut ",
        "fertilizer_class": "Oil seeds",
        "aliases": ["coconut", "coconut ", "nariyal"]
    },
    "cotton": {
        "canonical_id": "cotton",
        "display_name": "Cotton",
        "emoji": "🌿",
        "category": "Commercial",
        "yield_class": "Cotton(lint)",
        "fertilizer_class": "Cotton",
        "aliases": ["cotton", "cotton(lint)", "kapas"]
    },
    "jute": {
        "canonical_id": "jute",
        "display_name": "Jute",
        "emoji": "🌾",
        "category": "Commercial",
        "yield_class": "Jute",
        "fertilizer_class": "Cotton",
        "aliases": ["jute", "patson", "mesta", "jute & mesta"]
    },
    "coffee": {
        "canonical_id": "coffee",
        "display_name": "Coffee",
        "emoji": "☕",
        "category": "Plantation",
        "yield_class": "Coffee",
        "fertilizer_class": "Pulses",
        "aliases": ["coffee", "kafi"]
    }
}


# -----------------------------------------------------------------------------
# 2. Module 3: Fertilizer Target Crop Categories (11 Classes)
# -----------------------------------------------------------------------------
FERTILIZER_CROP_CLASSES: Dict[str, Dict[str, Any]] = {
    "Paddy": {
        "name": "Paddy",
        "display_name": "Paddy (Rice)",
        "emoji": "🌾",
        "description": "Wetland and upland rice crops"
    },
    "Wheat": {
        "name": "Wheat",
        "display_name": "Wheat",
        "emoji": "🌾",
        "description": "Rabi cereal wheat"
    },
    "Maize": {
        "name": "Maize",
        "display_name": "Maize (Corn)",
        "emoji": "🌽",
        "description": "Kharif and Rabi maize"
    },
    "Barley": {
        "name": "Barley",
        "display_name": "Barley",
        "emoji": "🌾",
        "description": "Cereal barley"
    },
    "Millets": {
        "name": "Millets",
        "display_name": "Millets (Bajra, Jowar, Ragi)",
        "emoji": "🌾",
        "description": "Nutritious coarse grains: Pearl millet, sorghum, finger millet"
    },
    "Pulses": {
        "name": "Pulses",
        "display_name": "Pulses (Chickpea, Lentil, Beans, Fruits)",
        "emoji": "🫘",
        "description": "Legumes, nitrogen-fixing crops, and horticultural crops"
    },
    "Ground Nuts": {
        "name": "Ground Nuts",
        "display_name": "Ground Nuts (Peanuts)",
        "emoji": "🥜",
        "description": "Peanuts and related leguminous oilseeds"
    },
    "Oil seeds": {
        "name": "Oil seeds",
        "display_name": "Oil seeds (Mustard, Sunflower, Soybean)",
        "emoji": "🌻",
        "description": "Commercial oilseed crops"
    },
    "Cotton": {
        "name": "Cotton",
        "display_name": "Cotton & Fibre Crops",
        "emoji": "🌿",
        "description": "Fibre and textile cash crops"
    },
    "Sugarcane": {
        "name": "Sugarcane",
        "display_name": "Sugarcane",
        "emoji": "🎋",
        "description": "Sugar and bio-energy commercial crops"
    },
    "Tobacco": {
        "name": "Tobacco",
        "display_name": "Tobacco",
        "emoji": "🍂",
        "description": "Commercial tobacco cultivation"
    }
}


# -----------------------------------------------------------------------------
# 3. Clean Display Names & Aliases for Yield Prediction (124 Classes)
# -----------------------------------------------------------------------------
YIELD_DISPLAY_OVERRIDES: Dict[str, str] = {
    "Coconut ": "Coconut",
    "Cotton(lint)": "Cotton",
    "Gram": "Chickpea (Gram)",
    "Arhar/Tur": "Pigeon Peas (Arhar/Tur)",
    "Moong(Green Gram)": "Mung Bean (Moong)",
    "Pome Granet": "Pomegranate",
    "Rajmash Kholar": "Kidney Beans (Rajma)",
    "Water Melon": "Watermelon / Melons",
    "Rice": "Rice (Paddy)",
    "Bajra": "Bajra (Pearl Millet)",
    "Jowar": "Jowar (Sorghum)",
    "Ragi": "Ragi (Finger Millet)",
    "Urad": "Urad (Blackgram)",
    "Masoor": "Masoor (Red Lentil)",
    "Soyabean": "Soybean",
    "Rapeseed &Mustard": "Mustard & Rapeseed",
    "Dry chillies": "Dry Chillies",
    "Dry ginger": "Dry Ginger",
    "Black pepper": "Black Pepper",
    "Sweet potato": "Sweet Potato",
    "Pump Kin": "Pumpkin",
    "Ash Gourd": "Ash Gourd",
    "Bottle Gourd": "Bottle Gourd",
    "Bitter Gourd": "Bitter Gourd",
    "Ribed Guard": "Ribbed Gourd",
    "Snak Guard": "Snake Gourd",
}


# -----------------------------------------------------------------------------
# 4. All 124 Exact Classes from Yield Crop Encoder
# -----------------------------------------------------------------------------
YIELD_CROP_CLASSES: tuple[str, ...] = (
    "Apple", "Arcanut (Processed)", "Arecanut", "Arhar/Tur", "Ash Gourd", "Atcanut (Raw)",
    "Bajra", "Banana", "Barley", "Bean", "Beans & Mutter(Vegetable)", "Beet Root", "Ber",
    "Bhindi", "Bitter Gourd", "Black pepper", "Blackgram", "Bottle Gourd", "Brinjal",
    "Cabbage", "Cardamom", "Carrot", "Cashewnut", "Cashewnut Processed", "Cashewnut Raw",
    "Castor seed", "Cauliflower", "Citrus Fruit", "Coconut ", "Coffee", "Colocosia",
    "Cond-spcs other", "Coriander", "Cotton(lint)", "Cowpea(Lobia)", "Cucumber",
    "Drum Stick", "Dry chillies", "Dry ginger", "Garlic", "Ginger", "Gram", "Grapes",
    "Groundnut", "Guar seed", "Horse-gram", "Jack Fruit", "Jobster", "Jowar", "Jute",
    "Jute & mesta", "Kapas", "Khesari", "Korra", "Lab-Lab", "Lemon", "Lentil",
    "Linseed", "Litchi", "Maize", "Mango", "Masoor", "Mesta", "Moong(Green Gram)",
    "Moth", "Niger seed", "Oilseeds total", "Onion", "Orange", "Other  Rabi pulses",
    "Other Cereals & Millets", "Other Citrus Fruit", "Other Dry Fruit",
    "Other Fresh Fruits", "Other Kharif pulses", "Other Vegetables", "Paddy",
    "Papaya", "Peach", "Pear", "Peas  (vegetable)", "Peas & beans (Pulses)",
    "Perilla", "Pineapple", "Plums", "Pome Fruit", "Pome Granet", "Potato",
    "Pulses total", "Pump Kin", "Ragi", "Rajmash Kholar", "Rapeseed &Mustard",
    "Redish", "Ribed Guard", "Rice", "Ricebean (nagadal)", "Rubber", "Safflower",
    "Samai", "Sannhamp", "Sapota", "Sesamum", "Small millets", "Snak Guard",
    "Soyabean", "Sugarcane", "Sunflower", "Sweet potato", "Tapioca", "Tea",
    "Tobacco", "Tomato", "Total foodgrain", "Turmeric", "Turnip", "Urad",
    "Varagu", "Water Melon", "Wheat", "Yam", "other fibres",
    "other misc. pulses", "other oilseeds"
)

# Build normalized mapping for fast case-insensitive lookup
_NORMALIZED_YIELD_MAP: Dict[str, str] = {
    c.strip().lower(): c for c in YIELD_CROP_CLASSES
}
for raw_crop, display_override in YIELD_DISPLAY_OVERRIDES.items():
    _NORMALIZED_YIELD_MAP[display_override.strip().lower()] = raw_crop


class CropManager:
    """Central authority for mapping and reconciling crops across all 3 modules."""

    @staticmethod
    def get_recommendation_crops() -> Dict[str, Dict[str, Any]]:
        """Return all 22 crop recommendation classes with their metadata."""
        return RECOMMENDATION_CROPS

    @staticmethod
    def resolve_for_yield(crop_input: Any) -> str:
        """
        Resolve any user input, recommendation crop, or alias into an exact
        class name present in `yield_crop_encoder.classes_` (124 classes).
        Handles empty strings, None, non-strings, and arbitrary unexpected strings safely.
        """
        if crop_input is None:
            return "Rice"

        cleaned = str(crop_input).strip().lower()
        if not cleaned or cleaned in ("none", "nan", "null", "undefined"):
            return "Rice"

        # 1. Direct check in recommendation crop registry
        if cleaned in RECOMMENDATION_CROPS:
            return RECOMMENDATION_CROPS[cleaned]["yield_class"]

        for data in RECOMMENDATION_CROPS.values():
            if cleaned == data["yield_class"].strip().lower():
                return data["yield_class"]
            if cleaned in [alias.strip().lower() for alias in data["aliases"]]:
                return data["yield_class"]

        # 2. Specific common synonyms / alternate spellings
        synonyms = {
            "chana": "Gram",
            "chickpea": "Gram",
            "chickpeas": "Gram",
            "cotton": "Cotton(lint)",
            "kapas": "Cotton(lint)",
            "coconut": "Coconut ",
            "melon": "Water Melon",
            "muskmelon": "Water Melon",
            "watermelon": "Water Melon",
            "pomegranate": "Pome Granet",
            "anar": "Pome Granet",
            "moong": "Moong(Green Gram)",
            "mung": "Moong(Green Gram)",
            "tur": "Arhar/Tur",
            "arhar": "Arhar/Tur",
            "toor": "Arhar/Tur",
            "rajma": "Rajmash Kholar",
            "rajmash": "Rajmash Kholar",
            "urad": "Blackgram",
            "paddy": "Rice",
            "soybean": "Soyabean",
            "mustard": "Rapeseed &Mustard",
            "groundnut": "Groundnut",
            "peanut": "Groundnut",
            "corn": "Maize",
        }
        if cleaned in synonyms:
            return synonyms[cleaned]

        # 3. Check against all 124 yield classes (and reverse display overrides)
        if cleaned in _NORMALIZED_YIELD_MAP:
            return _NORMALIZED_YIELD_MAP[cleaned]

        # 4. Try substring / partial match across 124 yield classes
        for norm_key, raw_class in _NORMALIZED_YIELD_MAP.items():
            if norm_key in cleaned or cleaned in norm_key:
                return raw_class

        # 5. Default fallback for completely unexpected / unmapped string:
        # Return a known, valid yield class ("Rice")
        return "Rice"

    @staticmethod
    def resolve_for_fertilizer(crop_input: Any) -> str:
        """
        Resolve any user input, yield crop, or recommendation crop into an exact
        category present in `crop_encoder.classes_` (11 fertilizer classes).
        Handles empty strings, None, non-strings, and arbitrary unexpected strings safely.
        """
        if crop_input is None:
            return "Paddy"

        cleaned = str(crop_input).strip().lower()
        if not cleaned or cleaned in ("none", "nan", "null", "undefined"):
            return "Paddy"

        # 1. Direct check in recommendation crops
        if cleaned in RECOMMENDATION_CROPS:
            return RECOMMENDATION_CROPS[cleaned]["fertilizer_class"]

        for data in RECOMMENDATION_CROPS.values():
            if cleaned in [alias.strip().lower() for alias in data["aliases"]]:
                return data["fertilizer_class"]

        # 2. Direct check against the 11 fertilizer classes
        for fert_name in FERTILIZER_CROP_CLASSES:
            if cleaned == fert_name.strip().lower():
                return fert_name

        # 3. Agricultural heuristics mapping from 124 yield crops to 11 fertilizer classes
        if any(k in cleaned for k in ["rice", "paddy", "dhan"]):
            return "Paddy"
        if "wheat" in cleaned:
            return "Wheat"
        if "barley" in cleaned:
            return "Barley"
        if any(k in cleaned for k in ["maize", "corn", "makka"]):
            return "Maize"
        if any(k in cleaned for k in ["cotton", "kapas"]):
            return "Cotton"
        if "tobacco" in cleaned:
            return "Tobacco"
        if "sugarcane" in cleaned:
            return "Sugarcane"
        if any(k in cleaned for k in ["groundnut", "ground nut", "peanut"]):
            return "Ground Nuts"
        if any(k in cleaned for k in ["millet", "bajra", "jowar", "ragi", "korra", "varagu", "samai", "jobster"]):
            return "Millets"
        if any(k in cleaned for k in ["oilseed", "sunflower", "sesamum", "soyabean", "soybean",
                                     "mustard", "rapeseed", "castor", "linseed", "niger",
                                     "safflower", "coconut", "perilla"]):
            return "Oil seeds"
        if any(k in cleaned for k in ["gram", "pulse", "arhar", "tur", "moong", "urad",
                                     "masoor", "moth", "bean", "pea", "khesari", "lobia"]):
            return "Pulses"

        # Horticultural crops, vegetables, fruits, and plantations default to general NPK complex (Pulses group)
        return "Pulses"

    @staticmethod
    def get_yield_dropdown_options(yield_crop_classes: List[str]) -> List[Dict[str, str]]:
        """
        Return structured dropdown options for Yield Prediction with user-friendly
        labels while preserving the exact dataset value for model prediction.
        """
        options = []
        for raw_crop in yield_crop_classes:
            raw_str = str(raw_crop)
            label = YIELD_DISPLAY_OVERRIDES.get(raw_str, raw_str)
            options.append({
                "value": raw_str,
                "label": label,
                "category": CropManager.resolve_for_fertilizer(raw_str)
            })

        # Sort alphabetically by display label
        return sorted(options, key=lambda x: x["label"].lower())

    @staticmethod
    def get_fertilizer_dropdown_options() -> List[Dict[str, str]]:
        """
        Return structured dropdown options for the Soil Health & Fertilizer page.
        Covers the 11 classes plus user-friendly entries for fruits, melons, and common crops.
        """
        return [
            {"value": "Paddy", "label": "🌾 Paddy / Rice", "group": "Cereals"},
            {"value": "Wheat", "label": "🌾 Wheat", "group": "Cereals"},
            {"value": "Maize", "label": "🌽 Maize (Corn)", "group": "Cereals"},
            {"value": "Barley", "label": "🌾 Barley", "group": "Cereals"},
            {"value": "Millets", "label": "🌾 Millets (Bajra, Jowar, Ragi)", "group": "Cereals"},
            {"value": "Pulses", "label": "🫘 Pulses (Chickpea, Lentil, Moong, Urad, Beans)", "group": "Pulses & Legumes"},
            {"value": "Ground Nuts", "label": "🥜 Ground Nuts (Peanuts)", "group": "Oilseeds"},
            {"value": "Oil seeds", "label": "🌻 Oil seeds (Mustard, Soybean, Sunflower)", "group": "Oilseeds"},
            {"value": "Cotton", "label": "🌿 Cotton & Fibre Crops", "group": "Cash & Commercial Crops"},
            {"value": "Sugarcane", "label": "🎋 Sugarcane", "group": "Cash & Commercial Crops"},
            {"value": "Tobacco", "label": "🍂 Tobacco", "group": "Cash & Commercial Crops"},
        ]

    @staticmethod
    def get_unified_crop_metadata() -> Dict[str, Any]:
        """Return full JSON-serializable taxonomy for client JavaScript consumption."""
        return {
            "recommendation_crops": RECOMMENDATION_CROPS,
            "fertilizer_categories": FERTILIZER_CROP_CLASSES,
            "yield_display_overrides": YIELD_DISPLAY_OVERRIDES,
        }
