from __future__ import annotations

import logging
import os
from functools import partial
from typing import TYPE_CHECKING

from flogin import Result
from flogin.jsonrpc.responses import ExecuteResponse

if TYPE_CHECKING:
    from .plugin import FirefoxKeywordBookmarks  # noqa: F401

log = logging.getLogger(__name__)


class Bookmark(Result["FirefoxKeywordBookmarks"]):
    def __init__(
        self,
        *,
        keyword: str,
        url: str,
        profile_path: str,
    ) -> None:
        super().__init__(title=keyword, sub=url, icon="assets/app.png", copy_text=url)
        self.profile_fp = profile_path
        self.keyword = keyword
        self.url = url

    async def callback(self) -> ExecuteResponse:
        assert self.plugin

        firefox_fp = self.plugin.firefox_fp

        if firefox_fp is None:
            await self.plugin.api.open_url(self.url)
        else:
            cmd = f'cd "{firefox_fp}" && "firefox.exe" "{self.url}" -profile "{self.profile_fp}"'
            log.debug("Running shell command: %r", cmd)
            await self.plugin.api.run_shell_cmd(cmd)
        return ExecuteResponse()

    async def context_menu(self):
        assert self.plugin

        return [
            Result.create_with_partial(
                partial(self.plugin.copy_text, self.keyword),
                title="Copy Keyword",
                icon="assets/app.png",
            ),
            Result.create_with_partial(
                partial(self.plugin.copy_text, self.url),
                title="Copy URL",
                icon="assets/app.png",
            ),
            Result.create_with_partial(
                partial(self.plugin.reload_cache),
                title="Reload Cache",
                icon="assets/app.png",
            ),
            Result.create_with_partial(
                partial(
                    self.plugin.api.open_directory,
                    os.getcwd(),
                    "FirefoxKeywordBookmarks.logs",
                ),
                title="Open Log File",
                sub="Open FirefoxKeywordBookmarks.log in explorer",
                icon="assets/app.png",
            ),
        ]
