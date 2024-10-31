import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "plugin"))

from Plugin.utils import setup_logging
from Plugin.core import FirefoxKeywordBookmarks

if __name__ == "__main__":
    setup_logging()
    FirefoxKeywordBookmarks()
