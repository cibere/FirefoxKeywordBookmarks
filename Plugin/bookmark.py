from __future__ import annotations

import logging
import os
from functools import partial
from typing import TYPE_CHECKING

from flogin import Result
from flogin.jsonrpc.responses import ExecuteResponse

if TYPE_CHECKING:
    from .plugin import FirefoxKeywordBookmarks

log = logging.getLogger(__name__)


class Bookmark(Result):
    plugin: FirefoxKeywordBookmarks  # type: ignore

    def __init__(
        self,
        *,
        keyword: str,
        url: str,
        profile_path: str,
    ) -> None:
        super().__init__(title=keyword, sub=url, icon="Images/app.png", copy_text=url)
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
            log.debug(f"Running shell command: {cmd!r}")
            await self.plugin.api.run_shell_cmd(cmd)
        return ExecuteResponse()

    async def context_menu(self):
        return [
            Result.create_with_partial(
                partial(self.plugin.copy_text, self.keyword), title="Copy Keyword", icon="Images/app.png"
            ),
            Result.create_with_partial(
                partial(self.plugin.copy_text, self.url), title="Copy URL", icon="Images/app.png"
            ),
            Result.create_with_partial(
                partial(self.plugin.reload_cache),
                title=f"Reload Cache",
                icon="Images/app.png",
            ),
            Result.create_with_partial(
                partial(
                    self.plugin.api.open_directory,
                    os.getcwd(),
                    "FirefoxKeywordBookmarks.logs",
                ),
                title="Open Log File",
                sub="Open FirefoxKeywordBookmarks.log in explorer",
                icon="Images/app.png",
            ),
        ]
