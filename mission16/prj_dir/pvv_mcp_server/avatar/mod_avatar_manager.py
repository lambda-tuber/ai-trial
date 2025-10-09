
from pvv_mcp_server.avatar.mod_avatar import AvatarWindow
from typing import Any
import json
import sys

_avatars = None
_avatar_cache: dict[str, AvatarWindow] = {}

def setup(avs: dict[int, Any]):
    global _avatars
    _avatars = avs

    for style_id, info in _avatars.items():
        if info["表示"]:
            get_avatar(style_id)


def get_avatar(style_id: int) -> AvatarWindow:
    avatar_conf = _avatars[style_id]
    key = json.dumps(avatar_conf, sort_keys=True)

    if key in _avatar_cache:
        return _avatar_cache[key]

    instance = AvatarWindow(
        avatar_conf["画像"],
        default_anime_key="立ち絵",
        flip=avatar_conf["反転"],
        scale_percent=avatar_conf["縮尺"],
        app_title="Claude",
        position=avatar_conf["位置"]
    )
    instance.update_position()
    instance.show()
    _avatar_cache[key] = instance

    return instance


# ----------------------------
if __name__ == "__main__":
  print("test")
