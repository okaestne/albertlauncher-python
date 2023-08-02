# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path

from albert import *

md_iid = '2.0'
md_version = "2.0"
md_name = "Emoji Picker"
md_description = "Find and copy emojis by name"
md_license = "GPL-3.0"
md_url = "https://github.com/albertlauncher/python/tree/master/emoji"
md_maintainers = "@tyilo"

# todo : use https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-annotations-full/annotations/de/


# class Plugin(PluginInstance, IndexQueryHandler):
class Plugin(PluginInstance, IndexQueryHandler):

    def __init__(self):
        IndexQueryHandler.__init__(self,
                                   id=md_id,
                                   name=md_name,
                                   description=md_description,
                                   defaultTrigger=':',
                                   synopsis='<emoji name>')
        PluginInstance.__init__(self, extensions=[self])

    def updateIndexItems(self):
        line_re = re.compile(
            r"""
            ^
            (?P<codepoints> .*\S)
            \s*;\s*
            (?P<status> \S+)
            \s*\#\s*
            (?P<emoji> \S+)
            \s*
            (?P<version> E\d+.\d+)
            \s*
            (?P<name> [^:]+)
            (?: : \s* (?P<modifier> .+))?
            \n
            $
            """,
            re.VERBOSE,
        )

        root_path = Path(__file__).parent
        alias_file_path = root_path / "aliases.json"
        emoji_file_path = root_path / "emoji-test.txt"

        with alias_file_path.open("r") as f:
            aliases = json.load(f)

        index_items = []
        with emoji_file_path.open("r") as f:
            for line in f:
                if m := line_re.match(line):
                    e = m.groupdict()
                    if e["status"] == "fully-qualified":
                        emoji = e['emoji']
                        identifier = e['name']
                        names = [identifier.capitalize(), *aliases.get(identifier, [])]
                        mod = e.get('modifier', None)

                        if mod:
                            title = f"{identifier.capitalize()} {mod}"
                        else:
                            title = identifier.capitalize()

                        item = StandardItem(
                            id=emoji,
                            text=title,
                            subtext=", ".join([a.capitalize() for a in names]),
                            iconUrls=[f"gen:?text={emoji}"],
                            actions=[
                                Action(
                                    "copy",
                                    "Copy to clipboard",
                                    lambda emj=emoji: setClipboardText(emj),
                                ),
                            ]
                        )

                        index_items.extend([IndexItem(item, f"{n} {mod}" if mod else n) for n in names])

        self.setIndexItems(index_items)
