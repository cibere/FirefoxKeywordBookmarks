import os
import sqlite3
from logging import getLogger

import pyperclip
from flogin import ExecuteResponse, Plugin

from .bookmark import Bookmark
from .settings import FKBSettings

LOG = getLogger("plugin")


class FirefoxKeywordBookmarks(Plugin[FKBSettings]):
    def __init__(self) -> None:
        self.cache: dict[str, Bookmark] | None = None
        super().__init__()

    @property
    def profile_path_data(self) -> list[str] | None:
        path = self.settings.profile_path_data
        if path:
            return path.split("\r\n")

    @property
    def firefox_fp(self) -> str | None:
        return self.settings.firefox_fp

    def get_bookmarks(self, profile_path: str) -> dict[str, Bookmark]:
        LOG.info("Getting bookmarks for %s", profile_path)
        final: dict[str, Bookmark] = {}

        if profile_path[1] == "|":
            prefix = profile_path[0]
            profile_path = profile_path[2:]
        else:
            prefix = ""

        with sqlite3.connect(os.path.join(profile_path, "places.sqlite")) as con:
            rows = con.execute(
                "SELECT * FROM moz_keywords",
            ).fetchall()
            for keyword_data in rows:
                LOG.debug("keyword_data=%r", keyword_data)
                if keyword_data:
                    place_id = keyword_data[2]
                    keyword = f"{prefix}{keyword_data[1]}"
                    place = con.execute(
                        "SELECT * FROM moz_places WHERE id = ?", (place_id,)
                    ).fetchone()
                    if place:
                        url = place[1]
                        final[keyword] = Bookmark(
                            keyword=keyword, url=url, profile_path=profile_path
                        )
        LOG.debug("Returning bookmarks: %r", final)
        return final

    async def reload_cache(self) -> ExecuteResponse:
        paths = self.profile_path_data
        if paths:
            self.cache = {}

            try:
                for path in paths:
                    self.cache.update(self.get_bookmarks(path))
            except sqlite3.OperationalError:
                await self.api.show_error_message(
                    "Firefox Keyword Bookmarks",
                    "Invalid Profile Data Path(s) given, run a new query for more information.",
                )
                self.cache = None
                return ExecuteResponse(False)

        await self.api.show_notification(
            "Firefox Keyword Bookmarks",
            "Cache successfully reloaded",
            "assets//app.png",
        )
        return ExecuteResponse(hide=False)

    async def copy_text(self, text: str) -> ExecuteResponse:
        pyperclip.copy(text)
        await self.api.show_notification(
            "Firefox Keyword Bookmarks",
            f"Successfully copied {text!r}",
            icon="assets/app.png",
        )
        return ExecuteResponse(hide=False)
