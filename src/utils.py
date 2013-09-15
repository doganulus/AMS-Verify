import itertools


def quoteifstr(s):
    if isinstance(s, str):
        return '"{}"'.format(s)
    else:
        return str(s)


def _nt(time_value):
    if time_value < 0.0:
        t = 0.0
    else:
        t = time_value
    return t


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def staircase(iterable):
    result = []
    for i in range(len(iterable)-1):
        result.append(iterable[i])
        result.append((iterable[i+1][0], iterable[i][1]))

    result.append(iterable[-1])
    return result

if __name__ == '__main__':
    pass
