import inspect
import json
import os
import sqlite3
import sys
import time
import webbrowser
from logging import getLogger
from typing import Any

from .dataclass import Dataclass
from .errors import BasePluginException, InternalException
from .options import Option

LOG = getLogger(__name__)


class FirefoxKeywordBookmarks:
    def __init__(self, args: str | None = None):
        # defalut jsonrpc
        self.rpc_request = {"method": "query", "parameters": [""]}
        start_time = time.perf_counter()

        if args is None and len(sys.argv) > 1:

            # Gets JSON-RPC from Flow Launcher process.
            self.rpc_request = json.loads(sys.argv[1])
        LOG.debug(f"Received RPC request: {json.dumps(self.rpc_request)}")

        # proxy is not working now
        # self.proxy = self.rpc_request.get("proxy", {})

        request_method_name = self.rpc_request.get("method", "query")
        request_parameters = self.rpc_request.get("parameters", [])

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        request_method = dict(methods)[request_method_name]
        if request_method_name in ("query", "context_menu"):
            try:
                raw_results = request_method(*request_parameters)
            except BasePluginException as e:
                raw_results = e.options
            except Exception as e:
                LOG.error(
                    f"Error happened while running {request_method_name!r} method.",
                    exc_info=e,
                )
                raw_results = InternalException().options
            final_results = []

            for result in raw_results:
                if isinstance(result, Dataclass):
                    result = result.to_option()
                if isinstance(result, Option):
                    result = result.to_jsonrpc()
                if isinstance(result, dict):
                    final_results.append(result)
                else:
                    LOG.error(
                        f"Unknown result given: {result!r}",
                        exc_info=RuntimeError(f"Unknown result given: {result!r}"),
                    )
                    final_results = InternalException().final_options()
                    break

            data = {"result": final_results}

            payload = json.dumps(data)
            LOG.debug(f"Sending data to flow: {payload}")
            print(payload)
        else:
            request_method(*request_parameters)
        end_time = time.perf_counter()
        LOG.info(f"Finished in {(end_time - start_time)*1000}ms")

    @property
    def settings(self) -> dict:
        return self.rpc_request["settings"]

    def get_bookmarks(self, profile_path: str) -> dict[str, dict]:
        final = {}

        with sqlite3.connect(os.path.join(profile_path, "places.sqlite")) as con:
            rows = con.execute(
                "SELECT * FROM moz_keywords",
            ).fetchall()
            for keyword_data in rows:
                LOG.debug(f"{keyword_data=}")
                if keyword_data:
                    place_id = keyword_data[2]
                    keyword = keyword_data[1]
                    place = con.execute(
                        "SELECT * FROM moz_places WHERE id = ?", (place_id,)
                    ).fetchone()
                    if place:
                        url = place[1]
                        final[keyword] = Option(
                            title=keyword,
                            sub=url,
                            callback="open_url",
                            params=[url],
                            score=100,
                        ).to_jsonrpc()
        return final

    def query(self, query: str):
        LOG.info(f"Received query: {query!r}")

        profile_path = (self.settings["profile_path"] or "").strip().strip('"')
        if not profile_path:
            return [
                Option(
                    title="Error: No profile data path given",
                    sub="Open context menu for more options",
                    context_data=[
                        Option(
                            title="Open Settings Menu", callback="open_settings_menu"
                        ),
                        Option(
                            title="Open Guide",
                            callback="open_url",
                            params=[
                                "https://github.com/cibere/Flow.Launcher.Plugin.FirefoxKeywordBookmarks?tab=readme-ov-file#how-to-get-profile-data-path"
                            ],
                        ),
                        Option(
                            title="Open Profiles",
                            callback="open_url",
                            params=["about:profiles"],
                        ),
                    ],
                )
            ]

        if not os.path.exists("cache.json") or query == ":!RELOAD-FKB":
            LOG.info("Reloading")
            cache = self.get_bookmarks(profile_path)
            with open("cache.json", "w", encoding="UTF-8") as f:
                json.dump(cache, f)
            LOG.info(f"Finished reloading cache. New Cache: {cache!r}")
            return [Option(title="Finished Reloading Bookmark Cache", score=100)]
        else:
            with open("cache.json", "r", encoding="UTF-8") as f:
                cache: dict[str, dict] = json.load(f)
            LOG.info(f"Got cache, cache: {cache!r}")
        opt = cache.get(query)
        if opt:
            return [opt]
        return []

    def context_menu(self, data: list[Any]):
        LOG.debug(f"Context menu received: {data=}")
        return data

    def open_url(self, url):
        webbrowser.open(url)

    def open_settings_menu(self):
        print(
            json.dumps({"method": "Flow.Launcher.OpenSettingDialog", "parameters": []})
        )

    def open_log_file_folder(self):
        log_fp = os.path.join(os.getcwd(), "FirefoxKeywordBookmarks.log")
        LOG.info(f"Log File: {log_fp}")
        os.system(f'explorer.exe /select, "{log_fp}"')
