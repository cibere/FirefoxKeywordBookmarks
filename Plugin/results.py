from functools import partial

from flogin import Result


class NoProfilePathResult(Result):
    def __init__(self) -> None:
        super().__init__(
            title="Error: No profile data path given",
            sub="Open context menu for more options",
            icon="assets/error.png",
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_settings_menu()

    async def context_menu(self):
        assert self.plugin

        return [
            Result.create_with_partial(
                self.plugin.api.open_settings_menu,
                title="Open Settings Menu",
                icon="assets/error.png",
            ),
            Result.create_with_partial(
                partial(
                    self.plugin.api.open_url,
                    "https://github.com/cibere/Flow.Launcher.Plugin.FirefoxKeywordBookmarks?tab=readme-ov-file#how-to-get-profile-data-path",
                ),
                title="Open Guide",
                icon="assets/github.png",
            ),
        ]


class InvalidProfilePathResult(Result):
    def __init__(self, path: str) -> None:
        super().__init__(
            title=f"Error: Unable to open profile database file. Profile: {path}",
            sub="Are you sure the profile exists and is correct? Click this to open settings menu, or open the context menu for more options.",
            icon="assets/error.png",
        )

    async def callback(self):
        assert self.plugin

        await self.plugin.api.open_settings_menu()

    async def context_menu(self):
        assert self.plugin

        return [
            Result.create_with_partial(
                self.plugin.api.open_settings_menu,
                title="Open Settings Menu",
                icon="assets/error.png",
            ),
            Result.create_with_partial(
                partial(
                    self.plugin.api.open_url,
                    "https://github.com/cibere/Flow.Launcher.Plugin.FirefoxKeywordBookmarks?tab=readme-ov-file#how-to-get-profile-data-path",
                ),
                title="Open Guide",
                icon="assets/github.png",
            ),
        ]
