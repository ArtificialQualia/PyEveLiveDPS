[toc]

# How does the translation works

### Apply a localized version

1. Place a localization file under `PyEveLiveDPS\lang`, or choose one existed there; the localization file looks like `lang_****.json` or `lang_****.jsonc`
2. Copy it to `\PyEveLiveDPS`, Rename it to `lang.json` or `lang.jsonc`. 
3. Restart PELD and it should work :)

### Create a new localized version

1. Find `models.jsonc` under `PyEveLiveDPS\lang`
2. `models.jsonc` is a model of almost all(as I may found) the strings you may see in PELD. You need to make a copy of it and rename it to your language, say, `lang_zh-CN.jsonc`.
3. Open your `lang_zh-CN.jsonc`. The "key" parts are the original strings in PELD GUI, your job is to translate the "value" parts from English into your language. Mind those `{0}` , `{1}`, etc. in the "key" strings, you need to keep them as-is in your translated "value" string.
4. After you finished translation, save the file. You have made a localization file of your own!

### Mechanics

This i18n solution made 2 modifications,

- create a `localization` module to process localization files, settings and strings, leave an interface function `tr()` for the GUI part;

- catch all strings in PELD GUI and wrap them each with `tr()` function.

  When `localization.py` is imported, it'll search `lang.jsonc`&`lang.json` in `PyEveLiveDPS`. If not found, it'll continue to search in `PyEveLiveDPS\lang`. If neither of the above contains such files, it'll use the original hard-coded built-in en-to-en5 translation(which obviously means displaying the string as-is).

Each time a widget needs to show a string in GUI, `tr()` would find the translation of the string in `lang.jsonc` and return it to GUI. There might be some decoding errors(though I've not seen any) that may need to be fixed in the future.