"""Per-user content picker that avoids repeats until the catalog is exhausted."""

from __future__ import annotations

import random
from typing import Optional

from .content import get_catalog
from .database import Database


def pick_unseen(
    db: Database,
    user_id: int,
    category: str,
    lang: str,
    *,
    record: bool = True,
) -> tuple[int, str]:
    """Pick a random item from ``category`` that the user hasn't seen yet.

    When every item has been shown, the seen list resets so the cycle starts
    over (so the user always gets *something* fresh-feeling). Returns
    ``(item_id, text)``.
    """
    catalog = get_catalog(category, lang)
    if not catalog:
        raise RuntimeError(f"Empty catalog for {category}/{lang}")

    seen = db.get_seen_ids(user_id, category)

    if len(seen) >= len(catalog):
        # Full loop done — reset history and pick fresh.
        db.reset_category(user_id, category)
        seen = set()

    candidates = [i for i in range(len(catalog)) if i not in seen]
    item_id = random.choice(candidates)

    if record:
        db.mark_seen(user_id, category, item_id)

    return item_id, catalog[item_id]


def pick_random(category: str, lang: str) -> str:
    """Cheap, non-personalised random pick (for scheduler previews / fallbacks)."""
    catalog = get_catalog(category, lang)
    return random.choice(catalog)


def progress(db: Database, user_id: int, category: str, lang: str) -> tuple[int, int]:
    """Return ``(seen, total)`` for UI display."""
    catalog = get_catalog(category, lang)
    seen = db.get_seen_ids(user_id, category)
    # Cap at total to avoid weirdness when category list shrinks between deploys.
    return min(len(seen), len(catalog)), len(catalog)
