from nintendo.nex import common

def test_datetime() -> common.DateTime:
    time = common.DateTime.now()
    print(time)


test_datetime()