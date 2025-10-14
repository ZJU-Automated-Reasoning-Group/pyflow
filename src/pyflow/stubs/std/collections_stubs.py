from __future__ import absolute_import

from ..stubcollector import stubgenerator

import collections


@stubgenerator
def makeCollectionsStubs(collector):
    llfunc = collector.llfunc
    export = collector.export
    attachPtr = collector.attachPtr

    @export
    @attachPtr(collections, "defaultdict")
    @llfunc
    def collections_defaultdict(default_factory, *args, **kwargs):
        # Create defaultdict with default_factory
        return allocate(collections.defaultdict)

    @export
    @attachPtr(collections, "Counter")
    @llfunc
    def collections_Counter(*args, **kwargs):
        # Create Counter object
        return allocate(collections.Counter)

    @export
    @attachPtr(collections, "OrderedDict")
    @llfunc
    def collections_OrderedDict(*args, **kwargs):
        # Create OrderedDict
        return allocate(collections.OrderedDict)

    @export
    @attachPtr(collections, "deque")
    @llfunc
    def collections_deque(iterable=None, maxlen=None):
        # Create deque
        return allocate(collections.deque)

    # deque methods
    @export
    @attachPtr(collections.deque, "append")
    @llfunc
    def deque_append(self, x):
        return allocate(type(None))

    @export
    @attachPtr(collections.deque, "appendleft")
    @llfunc
    def deque_appendleft(self, x):
        return allocate(type(None))

    @export
    @attachPtr(collections.deque, "pop")
    @llfunc
    def deque_pop(self):
        return allocate(object)  # Returns the popped element

    @export
    @attachPtr(collections.deque, "popleft")
    @llfunc
    def deque_popleft(self):
        return allocate(object)  # Returns the popped element

    @export
    @attachPtr(collections.deque, "extend")
    @llfunc
    def deque_extend(self, iterable):
        return allocate(type(None))

    @export
    @attachPtr(collections.deque, "extendleft")
    @llfunc
    def deque_extendleft(self, iterable):
        return allocate(type(None))
