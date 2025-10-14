from __future__ import absolute_import

from ..stubcollector import stubgenerator

import re


@stubgenerator
def makeREStubs(collector):
    llfunc = collector.llfunc
    export = collector.export
    attachPtr = collector.attachPtr

    @export
    @attachPtr(re, "search")
    @llfunc
    def re_search(pattern, string, flags=0):
        # Search for pattern in string, return Match object or None
        match_obj = allocate(type(re.search("test", "test")))  # Match object type
        if match_obj is not None:
            return match_obj
        return allocate(type(None))

    @export
    @attachPtr(re, "match")
    @llfunc
    def re_match(pattern, string, flags=0):
        # Match pattern at beginning of string
        match_obj = allocate(type(re.match("test", "test string")))
        if match_obj is not None:
            return match_obj
        return allocate(type(None))

    @export
    @attachPtr(re, "findall")
    @llfunc
    def re_findall(pattern, string, flags=0):
        # Find all matches, return list
        return allocate(list)

    @export
    @attachPtr(re, "finditer")
    @llfunc
    def re_finditer(pattern, string, flags=0):
        # Find all matches, return iterator
        return allocate(type(iter([])))

    @export
    @attachPtr(re, "compile")
    @llfunc
    def re_compile(pattern, flags=0):
        # Compile pattern, return Pattern object
        pattern_obj = allocate(type(re.compile("test")))
        return pattern_obj

    @export
    @attachPtr(re, "sub")
    @llfunc
    def re_sub(pattern, repl, string, count=0, flags=0):
        # Substitute matches
        return allocate(str)

    @export
    @attachPtr(re, "split")
    @llfunc
    def re_split(pattern, string, maxsplit=0, flags=0):
        # Split string by pattern
        return allocate(list)
