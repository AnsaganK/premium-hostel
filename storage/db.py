REVIEWS_STORAGE = {}

import json
from datetime import datetime
from pathlib import Path

REVIEWS_FILE = Path("reviews.json")


def load_reviews() -> dict:
    if REVIEWS_FILE.exists():
        with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_reviews(data: dict):
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_review(user_id: int, text: str, rating: int, templates: list[str]):
    data = load_reviews()
    uid = str(user_id)

    review = {
        "rating": rating,
        "text": text,
        "templates": templates,
        "timestamp": datetime.now().isoformat()
    }

    if uid not in data:
        data[uid] = []
    data[uid].append(review)

    save_reviews(data)
