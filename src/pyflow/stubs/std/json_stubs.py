from __future__ import absolute_import

from ..stubcollector import stubgenerator

import json


@stubgenerator
def makeJSONStubs(collector):
    llfunc = collector.llfunc
    export = collector.export
    attachPtr = collector.attachPtr

    @export
    @attachPtr(json, "loads")
    @llfunc
    def json_loads(s, **kwargs):
        # Parse JSON string to Python object
        return allocate(dict)  # Conservative - could be dict, list, str, etc.

    @export
    @attachPtr(json, "dumps")
    @llfunc
    def json_dumps(obj, **kwargs):
        # Convert Python object to JSON string
        return allocate(str)

    @export
    @attachPtr(json, "load")
    @llfunc
    def json_load(fp, **kwargs):
        # Parse JSON from file-like object
        return allocate(dict)

    @export
    @attachPtr(json, "dump")
    @llfunc
    def json_dump(obj, fp, **kwargs):
        # Write JSON to file-like object
        return allocate(type(None))  # Returns None
