from nintendo.nex import backend, settings
import anyio
import logging

logging.basicConfig(level=logging.INFO)

IP_ADDR = "127.0.0.1"
ACCESS_KEY = "ridfebb9"
NEX_VERSION = 20000

async def main():
	s = settings.load("friends")
	s.configure(ACCESS_KEY, NEX_VERSION)
	
	async with backend.connect(s, IP_ADDR, 6000) as be:
		async with be.login_guest() as client:
			logging.info("WORKING IG.")
			pass


anyio.run(main)
