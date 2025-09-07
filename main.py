import pathlib
import sys

root = pathlib.Path(__file__).parent
sys.path.extend(
    str(path) for path in (root / "lib", root / ".venv" / "lib" / "site-packages", root)
)

from firefoxkeywordbookmarks.core import plugin  # noqa: E402

plugin.run()
