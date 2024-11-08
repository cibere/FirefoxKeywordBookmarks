# Flow.Launcher.Plugin.FirefoxKeywordBookmarks
A plugin for flow launcher that lets you open firefox bookmarks from their keyword.

## Tips

Set the score value for the plugin to 10 or something similiar, so it is at the top of the results.

## Useage
Start typing the keyword in the flow launcher menu, and after some time, it will appear.
> [!NOTE]
> The current code is unfortunately fairly slow, but that is mainly due to this plugin being written in python, and using V1 of the plugin API. I am working with one of the developers of Flow Launcher to hopefully start using V2 of the plugin API, but this will have to do until then.
![Example Image](Images/example.png)

## How to get profile data path
1. Head to `about:profiles` in firefox.
2. Find the profile that has the bookmarks that you want to use.
3. Copy the root path.
![](Images/find_path_example.png)
4. Paste it into the settings menu

## Cache
If enabled, FirefoxKeywordBookmarks will grab all of your bookmarks, and put them in a cache file for easy and faster access (the cache system is about 2x the speed). To reload the cache, use the `:!RELOAD_FKB` command.