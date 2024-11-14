import asyncio
import os
import sqlite3
import time
from logging import getLogger
from typing import Any

from flowpy import (
    Action,
    ExecuteResponse,
    Option,
    Plugin,
    Query,
    QueryResponse,
    Settings,
)

LOG = getLogger("plugin")


class FirefoxKeywordBookmarks(Plugin):
    def __init__(self) -> None:
        self.cache: dict[str, Option] | None = None
        super().__init__()

    def get_bookmarks(self, profile_path: str, firefox_fp: str) -> dict[str, Option]:
        LOG.info(f"Getting bookmarks for {profile_path}")
        final: dict[str, Option] = {}

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
                LOG.debug(f"{keyword_data=}")
                if keyword_data:
                    place_id = keyword_data[2]
                    keyword = f"{prefix}{keyword_data[1]}"
                    place = con.execute(
                        "SELECT * FROM moz_places WHERE id = ?", (place_id,)
                    ).fetchone()
                    if place:
                        url = place[1]
                        final[keyword] = Option(
                            title=keyword,
                            sub=url,
                            action=Action(self.open_url, firefox_fp, profile_path, url),
                            context_data=[profile_path, firefox_fp, []],
                            icon="Images/app.png",
                        )
        LOG.info(f"Returning bookmarks: {final!r}")
        return final

    async def __call__(self, data: Query, settings: Settings):
        now = time.perf_counter()
        query = data.text
        LOG.info(f"Received query: {query!r}")

        profile_path_data = settings.profile_path_data.strip().strip('"')
        if not profile_path_data:
            return [
                Option(
                    title="Error: No profile data path given",
                    sub="Open context menu for more options",
                    context_data=[
                        Option(
                            title="Open Settings Menu",
                            action=Action(self.api.open_settings_menu),
                        ),
                        Option(
                            title="Open Guide",
                            action=Action(
                                self.api.open_url,
                                "https://github.com/cibere/Flow.Launcher.Plugin.FirefoxKeywordBookmarks?tab=readme-ov-file#how-to-get-profile-data-path",
                            ),
                        ),
                    ],
                )
            ]

        if self.cache is None:
            self.cache = {}
            for path in profile_path_data.split("\\r\\n"):
                try:
                    self.cache.update(self.get_bookmarks(path, settings.firefox_fp))
                except sqlite3.OperationalError:
                    return [
                        Option(
                            f"Error: Unable to open profile database file. Profile: {path}",
                            sub="Are you sure the profile exists and is correct? Click this to open settings menu.",
                            action=Action(self.api.open_settings_menu),
                        )
                    ]
            LOG.info(f"Cache has been reloaded. {self.cache!r}")
        opt = self.cache.get(query)
        LOG.info(f"Finished in {(time.perf_counter() - now)*1000}ms")
        if opt:
            return [opt]
        return []

    async def context_menu(self, data: list[Any]):
        LOG.debug(f"Context menu received: {data=}")
        profile_path, firefox_fp, options = data
        return QueryResponse(
            options
            + [
                Option(
                    "Reload Cache",
                    icon="Images/app.png",
                    action=Action(self.reload_cache, profile_path, firefox_fp),
                ),
                Option(
                    "Open log file",
                    icon="Images/app.png",
                    sub="Open FirefoxKeywordBookmarks.log in explorer",
                    action=Action(self.open_log_file_folder),
                ),
            ]
        )

    async def open_log_file_folder(self):
        log_fp = os.path.join(os.getcwd(), "FirefoxKeywordBookmarks.logs")
        LOG.info(f"Log File: {log_fp}")
        cmd = f'explorer.exe /select, "{log_fp}"'
        LOG.debug(f"Running shell command: {cmd!r}")
        await self.api.run_shell_cmd(cmd)
        return ExecuteResponse()

    async def reload_cache(self, path: str, firefox_fp: str) -> ExecuteResponse:
        self.cache = self.get_bookmarks(path, firefox_fp)
        await self.api.show_message(
            "Firefox Keyword Bookmarks",
            "Cache successfully reloaded",
            "Images//app.png",
        )
        return ExecuteResponse(False)

    async def open_url(
        self, firefox_fp: str | None, profile_path: str | None, url: str
    ) -> ExecuteResponse:
        if firefox_fp is None:
            await self.api.open_url(url)
        else:
            cmd = (
                f'cd "{firefox_fp}" && "firefox.exe" "{url}" -profile "{profile_path}"'
            )
            LOG.debug(f"Running shell command: {cmd!r}")
            data = await self.api.run_shell_cmd(cmd)
            LOG.info(f"{data.data!r}")
        return ExecuteResponse()
