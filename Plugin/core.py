import logging
import sqlite3
import time
from typing import Any

from flogin import Query, Result

from .plugin import FirefoxKeywordBookmarks
from .results import InvalidProfilePathResult, NoProfilePathResult

log = logging.getLogger(__name__)

plugin = FirefoxKeywordBookmarks()

@plugin.search()
async def search_handler(data: Query):
    now = time.perf_counter()
    query = data.text
    log.info(f"Received query: {query!r}")

    cached_res = plugin.search_cache.get(query)
    if cached_res:
        log.info(f"Returning from cache: {cached_res}")
        return cached_res

    profile_path_data = plugin.profile_path_data

    if not profile_path_data:
        res = NoProfilePathResult()
        log.info(f"Returning invalid profile result: {res.slug}, {res!r}")
        return res

    log.info("Checking if cache is there")

    if plugin.cache is None:
        log.info(f"Reloading cache")
        plugin.cache = {}
        plugin.search_cache.clear()
        for path in profile_path_data:
            try:
                plugin.cache.update(plugin.get_bookmarks(path))
            except sqlite3.OperationalError:
                plugin.cache = None
                return InvalidProfilePathResult(path)

        log.info(f"Cache has been reloaded. {plugin.cache!r}")

    mark = plugin.cache.get(query)
    log.info(f"Finished in {(time.perf_counter() - now)*1000}ms")
    if mark:
        res = [mark]
    else:
        res = []
    plugin.search_cache[data.text] = res
    return res
