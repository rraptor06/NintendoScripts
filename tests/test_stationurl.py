from nintendo.nex import common

async def test_station_url() -> common.StationURL:
	url = common.StationURL(
		scheme="prudps", address="127.0.0.1", port=1224,
		PID = 2, CID = 1, type = 2,
    	sid = 1, stream = 10
	)

	print(url)


test_station_url()