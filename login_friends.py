from nintendo.nex import backend, settings
import anyio

import logging
logging.basicConfig(level=logging.INFO)

ACCESS_KEY: str = "ridfebb9"
NEX_VERSION: int = 200

async def main():
	s = settings.load("friends")
	s.configure(ACCESS_KEY, NEX_VERSION)
	
	async with backend.connect(s, "212.227.58.3", 6000) as be:
		async with be.login_guest() as client:
			logging.info("WORKING IG.")
			pass


anyio.run(main)
