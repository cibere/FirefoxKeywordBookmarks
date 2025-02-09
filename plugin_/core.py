import logging
import sqlite3
import time

from flogin import Query

from .plugin import FirefoxKeywordBookmarks
from .results import InvalidProfilePathResult, NoProfilePathResult

log = logging.getLogger(__name__)

plugin = FirefoxKeywordBookmarks()


@plugin.search()
async def search_handler(data: Query):
    now = time.perf_counter()
    query = data.text

    profile_path_data = plugin.profile_path_data

    if not profile_path_data:
        return NoProfilePathResult()

    if plugin.cache is None:
        log.info("Reloading cache")
        plugin.cache = {}
        path = ""

        try:
            for path in profile_path_data:
                plugin.cache.update(plugin.get_bookmarks(path))
        except sqlite3.OperationalError:
            plugin.cache = None
            return InvalidProfilePathResult(path)

        log.info("Cache has been reloaded. %r", plugin.cache)

    log.info("Finished in %sms", (time.perf_counter() - now) * 1000)
    return plugin.cache.get(query, [])
