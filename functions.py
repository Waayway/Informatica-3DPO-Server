def without_keys(d: dict, keys: list):
    return {x: d[x] for x in d if x not in keys}