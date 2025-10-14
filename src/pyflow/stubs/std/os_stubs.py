from __future__ import absolute_import

from ..stubcollector import stubgenerator

import os


@stubgenerator
def makeOSStubs(collector):
    llfunc = collector.llfunc
    export = collector.export
    fold = collector.fold
    staticFold = collector.staticFold
    attachPtr = collector.attachPtr

    # Path operations
    @export
    @attachPtr(os.path, "join")
    @llfunc
    def os_path_join(*paths):
        # Return a string representing the joined path
        return allocate(str)

    @export
    @attachPtr(os.path, "exists")
    @llfunc
    def os_path_exists(path):
        # Return boolean indicating if path exists
        return allocate(bool)

    @export
    @attachPtr(os.path, "isfile")
    @llfunc
    def os_path_isfile(path):
        return allocate(bool)

    @export
    @attachPtr(os.path, "isdir")
    @llfunc
    def os_path_isdir(path):
        return allocate(bool)

    @export
    @attachPtr(os.path, "basename")
    @llfunc
    def os_path_basename(path):
        return allocate(str)

    @export
    @attachPtr(os.path, "dirname")
    @llfunc
    def os_path_dirname(path):
        return allocate(str)

    # Environment operations
    @export
    @attachPtr(os, "getenv")
    @llfunc
    def os_getenv(key, default=None):
        return allocate(str)

    @export
    @attachPtr(os, "environ")
    @llfunc
    def os_environ_get(key):
        return allocate(str)

    # File operations
    @export
    @attachPtr(os, "listdir")
    @llfunc
    def os_listdir(path="."):
        return allocate(list)

    # Process operations
    @export
    @attachPtr(os, "getpid")
    @llfunc
    def os_getpid():
        return allocate(int)

    @export
    @attachPtr(os, "getcwd")
    @llfunc
    def os_getcwd():
        return allocate(str)
