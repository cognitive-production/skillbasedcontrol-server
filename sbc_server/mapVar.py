import copy
from dataclasses import asdict, is_dataclass


# initalize target.arrays/list with at least one element!
def mapVar(source, target, ignorekeys: list[str] = [], maxListLength=0):
    """map var to other var

    Args:
        source (): get data from this var.
        target (): set data to this var
        ignorekeys (list[str], optional): list of object keys/attr to ignore. Defaults to [].
        maxListLength (int, optional): max list length when copying lists. Defaults to 0.

    Returns:
        _type_: target var (reference)
    """
    if hasattr(source, "__dict__"):
        mapObject(source, target, ignorekeys, maxListLength)
    elif isinstance(source, list):
        mapList(source, target, ignorekeys, maxListLength)
    else:
        target = copy.deepcopy(source)
    return target


def mapObject(source: object, target: object, ignorekeys=[], maxListLength=0):
    """map object (dataclass) to other object (dataclass)

    Args:
        source (): get data from this object.
        target (): set data to this object
        ignorekeys (list[str], optional): list of object keys/attr to ignore. Defaults to [].
        maxListLength (int, optional): max list length when copying lists. Defaults to 0.
    """
    sourcedict = asdict(source) if is_dataclass(source) else source.__dict__
    for key, value in sourcedict.items():
        # for key, value in source.__dict__.items():
        targetdict = asdict(target) if is_dataclass(target) else target.__dict__
        if key in targetdict and not key in ignorekeys:
            if hasattr(getattr(source, key), "__dict__"):
                mapObject(
                    getattr(source, key),
                    getattr(target, key),
                    ignorekeys,
                    maxListLength,
                )
            elif isinstance(value, list):
                mapList(
                    getattr(source, key),
                    getattr(target, key),
                    ignorekeys,
                    maxListLength,
                )
            else:
                setattr(target, key, copy.deepcopy(value))


def mapList(source: list, target: list, ignorekeys=[], maxListLength=0):
    """map list to other list

    Args:
        source (): get data from this list.
        target (): set data to this list
        ignorekeys (list[str], optional): list of object keys/attr to ignore. Defaults to [].
        maxListLength (int, optional): max list length when copying lists. Defaults to 0.
    """
    for i in range(len(source)):
        if i + 1 > len(target):
            if i < maxListLength:
                target.append(copy.deepcopy(target[i - 1]))
            else:
                return
        if hasattr(source[i], "__dict__"):
            mapObject(source[i], target[i], ignorekeys, maxListLength)
        elif isinstance(source[i], list):
            mapList(source[i], target[i], ignorekeys, maxListLength)
        else:
            target[i] = copy.deepcopy(source[i])
