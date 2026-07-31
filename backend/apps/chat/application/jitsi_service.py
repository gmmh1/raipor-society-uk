import time

import jwt
from django.conf import settings


def mint_jitsi_token(*, room: str, user, moderator: bool = True, ttl_seconds: int = 7200) -> str:
    """Signs a Jitsi-compatible JWT (HS256, the standard prosody-mod-auth-jwt shape)
    for the given room. Any application holding ``settings.JITSI_APP_SECRET`` can
    mint an equally valid token the same way — that shared secret, not this
    function, is what makes video calling reusable outside this codebase. See the
    "Video calling" section of README.md for the exact payload other apps need to
    replicate.
    """
    now = int(time.time())
    payload = {
        "iss": settings.JITSI_APP_ID,
        "aud": settings.JITSI_APP_ID,
        "sub": settings.JITSI_DOMAIN,
        "room": room,
        "nbf": now - 10,
        "exp": now + ttl_seconds,
        "context": {
            "user": {
                "id": str(user.id),
                "name": (f"{user.first_name} {user.last_name}".strip() or user.username),
                "email": user.email,
                "moderator": moderator,
            }
        },
    }
    return jwt.encode(payload, settings.JITSI_APP_SECRET, algorithm="HS256")


def room_name_for_channel(channel_id) -> str:
    return f"raipur-society-uk-{channel_id}"
