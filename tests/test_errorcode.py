from nintendo.nex import common

def test_errorcode(error: bool = False) -> common.Result:
    if error:
        return common.Result.error("Authentication::UnderMaintenance")
    return common.Result.success()


test_errorcode()