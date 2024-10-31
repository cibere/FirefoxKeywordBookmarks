import json

with open("plugin.json", "r") as f:
    data = json.load(f)

data['ID'] = "28ff3a2e-7b21-4cd8-aeb8-3df34985c903"
data['Name'] = "Firefox Keyword Bookmarks"
data['Website'] = f"https://github.com/cibere/Flow.Launcher.Plugin.FirefoxKeywordBookmarks/tree/v{data['Version']}"
data['ActionKeyword'] = "*"

with open("plugin.json", "w") as f:
    json.dump(data, f)

print("New plugin.json contents:")
print(json.dumps(data, indent=4))