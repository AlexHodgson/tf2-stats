def bisect_dicts_left(a, x, key, lo=0, hi=None):
    """
    See https://github.com/python/cpython/blob/3.8/Lib/bisect.py
    Except for a key contained in dictionaries in a list sorted on that key
    """


    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid][key] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def bisect_dicts_right(a, x, key, lo=0, hi=None):
    """
    See https://github.com/python/cpython/blob/3.8/Lib/bisect.py
    Except for a key contained in dictionaries in a list sorted on that key
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid][key]:
            hi = mid
        else:
            lo = mid + 1
    return lo