import inspect
import json
import os
import sqlite3, time
import sys
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

    def get_bookmark(self, query: str, profile_path: str) -> list[Option]:
        opts = []

        with sqlite3.connect(os.path.join(profile_path, "places.sqlite")) as con:
            keyword_data = con.execute(
                "SELECT * FROM moz_keywords WHERE keyword = ?", (query,)
            ).fetchone()
            LOG.debug(f"{keyword_data=}")
            if keyword_data:
                place_id = keyword_data[2]
                keyword = keyword_data[1]
                place = con.execute(
                    "SELECT * FROM moz_places WHERE id = ?", (place_id,)
                ).fetchone()
                if place:
                    url = place[1]
                    opts.append(
                        Option(
                            title=keyword,
                            sub=url,
                            callback="open_url",
                            params=[url],
                            score=100,
                        )
                    )
        return opts

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

        if query.startswith(":"):
            LOG.info("Heading to get bookmark method")
            return self.get_bookmark(query, profile_path)
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
        os.system(f'explorer.exe /select, "FirefoxKeywordBookmarks.logs"')
