# ahadevtools

Custom Dalamud plugin repository for ahadev's FFXIV plugins.

## Add the repository

1. In game, type `/xlsettings` and open the **Experimental** tab.
2. Paste this URL into **Custom Plugin Repositories**, press **+**, then **Save**:

   ```
   https://raw.githubusercontent.com/AHAKuo/ahadevtools/main/pluginmaster.json
   ```

3. Open `/xlplugins` and search for the plugin you want.

## Plugins

| Plugin | Description | Source |
|---|---|---|
| Polite Eorzea | Say hello and thank your party with `/hi` and `/bye`, or automatically in duties. | [FFXIVPoliteEorzea](https://github.com/AHAKuo/FFXIVPoliteEorzea) |
| BladUI | Baldur's Gate-style inventory: multiselect, bulk move, one-click armoury cleanup. | [FFXIVBladUI](https://github.com/AHAKuo/FFXIVBladUI) |
| XMapper | Fill your cross hotbars for any job in one click, following a layout bias. | [FFXIVXMapper](https://github.com/AHAKuo/FFXIVXMapper) |

## How it works

`pluginmaster.json` is generated, not hand-edited. `plugins.json` lists the GitHub repositories to include. A GitHub Action rebuilds the manifest from each repository's latest release on every push, every six hours, and on demand.

Each plugin release must attach two assets from the Dalamud SDK build output (`bin/Release/<Name>/`):

- `latest.zip`
- `<InternalName>.json`

## Adding a plugin

1. Publish a GitHub release on the plugin repository with the two assets above.
2. Add `"owner/repo"` to `plugins.json` here and push, or run the **Update pluginmaster** workflow.

To refresh right after a new release instead of waiting for the schedule:

```
gh workflow run update-pluginmaster.yml -R AHAKuo/ahadevtools
```
