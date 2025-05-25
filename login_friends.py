from nintendo.nex import backend, settings
import anyio

import logging
logging.basicConfig(level=logging.INFO)


async def main():
	s = settings.load("friends")
	s.configure("ridfebb9", 20000)
	
	async with backend.connect(s, "212.227.58.3", 6000) as be:
		async with be.login_guest() as client:
			logging.info("WORKING IG.")
			pass

anyio.run(main)
