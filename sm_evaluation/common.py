__author__ = 'ugonzjo'
def pretty(x):
    if isinstance(x, dict):
        ans = []
        for (k, v) in x.items():
            ans.append("{}:{}".format(k, pretty(v)))
        return "{" + ",".join(ans) + "}"
    elif isinstance(x, list):
        return "[" + ", ".join([pretty(e) for e in x]) + "]"
    elif isinstance(x, float):
        return "%4.3f" % x
    else:
        return str(x)

def intstr(x):
    return str(int(x))
