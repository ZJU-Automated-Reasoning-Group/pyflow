from __future__ import absolute_import

from ..stubcollector import stubgenerator

import itertools


@stubgenerator
def makeItertoolsStubs(collector):
    llfunc = collector.llfunc
    export = collector.export
    attachPtr = collector.attachPtr

    @export
    @attachPtr(itertools, "count")
    @llfunc
    def itertools_count(start=0, step=1):
        # Create infinite iterator starting from start
        return allocate(type(itertools.count()))

    @export
    @attachPtr(itertools, "cycle")
    @llfunc
    def itertools_cycle(iterable):
        # Cycle through iterable elements infinitely
        return allocate(type(itertools.cycle([1, 2, 3])))

    @export
    @attachPtr(itertools, "repeat")
    @llfunc
    def itertools_repeat(object, times=None):
        # Repeat object, optionally limited times
        return allocate(type(itertools.repeat(1)))

    @export
    @attachPtr(itertools, "chain")
    @llfunc
    def itertools_chain(*iterables):
        # Chain multiple iterables together
        return allocate(type(itertools.chain([1, 2], [3, 4])))

    @export
    @attachPtr(itertools, "islice")
    @llfunc
    def itertools_islice(iterable, stop):
        # Slice iterator
        return allocate(type(itertools.islice([1, 2, 3, 4], 2)))

    @export
    @attachPtr(itertools, "tee")
    @llfunc
    def itertools_tee(iterable, n=2):
        # Create n independent iterators from iterable
        return allocate(tuple)  # Returns tuple of iterators

    @export
    @attachPtr(itertools, "zip_longest")
    @llfunc
    def itertools_zip_longest(*iterables, fillvalue=None):
        # Zip iterables, filling shorter ones with fillvalue
        return allocate(type(itertools.zip_longest([1, 2], [3])))

    @export
    @attachPtr(itertools, "product")
    @llfunc
    def itertools_product(*iterables, repeat=1):
        # Cartesian product of iterables
        return allocate(type(itertools.product([1, 2], [3, 4])))

    @export
    @attachPtr(itertools, "permutations")
    @llfunc
    def itertools_permutations(iterable, r=None):
        # All permutations of iterable
        return allocate(type(itertools.permutations([1, 2, 3])))

    @export
    @attachPtr(itertools, "combinations")
    @llfunc
    def itertools_combinations(iterable, r):
        # All combinations of iterable elements
        return allocate(type(itertools.combinations([1, 2, 3], 2)))

    @export
    @attachPtr(itertools, "combinations_with_replacement")
    @llfunc
    def itertools_combinations_with_replacement(iterable, r):
        # Combinations with replacement
        return allocate(type(itertools.combinations_with_replacement([1, 2], 2)))
