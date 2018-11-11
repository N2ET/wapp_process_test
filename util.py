def apply_if(target, extra):
    for k, v in extra.items():
        if k not in target:
            target[k] = v