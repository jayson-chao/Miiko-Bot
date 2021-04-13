# parse_args.py
# methods to parse tag/string args for commands

import re
from typing import Set

_tag_re = re.compile(r'(\$[^\s]+) ?')

def parse_arguments(args):
    args = args.lower()
    tags = [t[1:] for t in _tag_re.findall(args)] # get each tag, strip '$' from beginning
    args = _tag_re.sub('', args).strip() # remove tags from the args
    return ParsedArguments(args, tags)

class ParsedArguments:
    text: str
    tags: Set[str]
    words: Set[str]

    def __init__(self, text, tags):
        self.text = text
        self.tags = tags
        self.words = text.split()

    def has_word(self, word):
        return value in self.words

    def has_tag(self, tag):
        return tag in self.tags