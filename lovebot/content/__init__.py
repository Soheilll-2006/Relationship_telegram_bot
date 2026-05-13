"""Curated content for LoveBot — quotes, advice, challenges, compliments.

Each module exports two parallel lists (``fa`` and ``en``) so the catalogue
is the same size in both languages and items map one-to-one by index when
that matters. The bot uses each item's *list index* as a stable
``item_id`` for the no-repeat mechanism.
"""

from . import quotes, advice, challenges, compliments, greetings  # noqa: F401

__all__ = ["quotes", "advice", "challenges", "compliments", "greetings"]


def get_catalog(category: str, lang: str) -> list[str]:
    """Return the list of items for ``category`` in ``lang``.

    Categories: ``quotes``, ``advice``, ``challenges``, ``compliments``.
    """
    mapping = {
        "quotes": quotes,
        "advice": advice,
        "challenges": challenges,
        "compliments": compliments,
    }
    mod = mapping[category]
    return getattr(mod, lang.upper())
