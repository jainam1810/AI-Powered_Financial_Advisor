import re

# ---------------------------
# Normalize raw merchant text
# ---------------------------


def normalize_merchant(text: str) -> str:
    if not isinstance(text, str):
        return "UNKNOWN"

    text = text.upper()

    # Remove numbers (store ids, refs)
    text = re.sub(r"\d+", "", text)

    # Remove symbols
    text = re.sub(r"[^A-Z ]", " ", text)

    # Remove noise words
    noise_words = [
        "CONTACTLESS", "ONLINE", "UK", "LONDON",
        "MANCHESTER", "PAYMENT", "CARD"
    ]
    for word in noise_words:
        text = text.replace(word, "")

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------
# Brand mapping (Open Banking style)
# ---------------------------
BRAND_MAP = {
    "APPLE": "Apple Services",
    "ITUNES": "Apple Services",
    "NETFLIX": "Netflix",
    "SPOTIFY": "Spotify",
    "AMAZON": "Amazon",
    "TESCO": "Tesco",
    "SAINSBURY": "Sainsbury's",
    "ASDA": "ASDA",
    "ALDI": "Aldi",
    "LIDL": "Lidl",
    "ARGOS": "Argos",
    "H&M": "H&M",
    "ZARA": "Zara",
    "UBER": "Uber",
    "TRAINLINE": "Trainline",
    "TFL": "Transport for London",
}


def map_to_brand(merchant_clean: str) -> str:
    if not merchant_clean:
        return "Unknown"

    for key, brand in BRAND_MAP.items():
        if key in merchant_clean:
            return brand

    # Safe fallback
    return merchant_clean.split(" ")[0].title()
