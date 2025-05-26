from nintendo.nex import rmc, kerberos, friends, \
	authentication, common, settings, secure, matchmaking
from anyio import Lock
import collections
import secrets
import aioconsole
import asyncio

import logging
logging.basicConfig(level=logging.INFO)

ACCESS_KEY = "ridfebb9"
NEX_VERSION = 20000
SECURE_SERVER = "Quazal Rendez-Vous"
BUILD_STRING = "NEX Friends Server"

User = collections.namedtuple("User", "pid name password")

users = [
	User(2, "Quazal Rendez-Vous", "password"),
	User(100, "guest", "MMQea3n!fsik")
]

def get_user_by_name(name):
	for user in users:
		if user.name == name:
			return user
			
def get_user_by_pid(pid):
	for user in users:
		if user.pid == pid:
			return user
			
def derive_key(user):
	deriv = kerberos.KeyDerivationOld(65000, 1024)
	return deriv.derive_key(user.password.encode("ascii"), user.pid)


class AuthenticationServer(authentication.AuthenticationServer):
	def __init__(self, settings):
		super().__init__()
		self.settings = settings
	
	async def login(self, client, username):
		print("User trying to log in:", username)
		
		user = get_user_by_name(username)
		if not user:
			raise common.RMCError("RendezVous::InvalidUsername")
			
		server = get_user_by_name(SECURE_SERVER)
		
		url = common.StationURL(
			scheme="prudps", address="127.0.0.1", port=1224,
			PID = server.pid, CID = 1, type = 2,
			sid = 1, stream = 10
		)
		
		conn_data = authentication.RVConnectionData()
		conn_data.main_station = url
		conn_data.special_protocols = []
		conn_data.special_station = common.StationURL()
		
		response = rmc.RMCResponse()
		response.result = common.Result.success()
		response.pid = user.pid
		response.ticket = self.generate_ticket(user, server)
		response.connection_data = conn_data
		response.server_name = BUILD_STRING
		return response
	
	async def login_ex(self, client, username, extra_data):
		return self.login(client, username)
		
	def generate_ticket(self, source, target):
		settings = self.settings
		
		user_key = derive_key(source)
		server_key = derive_key(target)
		session_key = secrets.token_bytes(settings["kerberos.key_size"])
		
		internal = kerberos.ServerTicket()
		internal.timestamp = common.DateTime.now()
		internal.source = source.pid
		internal.session_key = session_key
		
		ticket = kerberos.ClientTicket()
		ticket.session_key = session_key
		ticket.target = target.pid
		ticket.internal = internal.encrypt(server_key, settings)
		
		return ticket.encrypt(user_key, settings)
		

class SecureServer(secure.SecureConnectionServer):
	def __init__(self, settings):
		super().__init__()
		self.settings = settings
		self.connection_id_counter = 1
		self.connection_id_lock = Lock()
		self.clients = {}

	async def register(self, client: rmc.RMCClient, urls: list[common.StationURL]):
		addr = client.remote_address()
		station = urls[0].copy()
		
		async with self.connection_id_lock:
			cid = self.connection_id_counter
			client.client.user_cid = cid
			self.clients[cid] = client

			self.connection_id_counter += 1
	
		station["address"] = addr[0]
		station["port"] = addr[1]
		station["natf"] = 0
		station["natm"] = 0
		station["type"] = 3
		station["PID"] = client.pid()

		response = rmc.RMCResponse()
		response.result = common.Result.success()
		response.connection_id = cid
		response.public_station = station

		return response

	async def register_ex(self, client: rmc.RMCClient, urls: list[common.StationURL], login_data):
		return await self.register(client, urls)
	

class FriendsServer3DS(friends.FriendsServerV1):
	def __init__(self, settings):
		super().__init__()
		self.settings = settings


class FriendsServerWiiU(friends.FriendsServerV2):
	def __init__(self, settings):
		super().__init__()
		self.settings = settings

	def add_friend_request(self, client):
		pass


async def main():
	s = settings.load("friends")
	s.configure(ACCESS_KEY, NEX_VERSION)
	
	auth_servers = [
		AuthenticationServer(s),
	]
	secure_servers = [
		SecureServer(s),
		FriendsServer3DS(s),
		FriendsServer3DS(s),
	]
	
	server_key = derive_key(get_user_by_name(SECURE_SERVER))
	async with rmc.serve(s, auth_servers, "127.0.0.1", 1223):
		async with rmc.serve(s, secure_servers, "127.0.0.1", 1224, key=server_key):
			await aioconsole.ainput("Press enter to exit...\n")


asyncio.run(main())
