def error_m(error):
    ans = error.copy()
    while isinstance(ans, dict):
        ans = next(iter(ans))
        key = ans
        ans = error[ans]
        error = ans.copy()
    return key + ": " + ans[0]
