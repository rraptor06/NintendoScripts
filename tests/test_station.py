from nintendo.nex import common
import collections

SECURE_SERVER = "Quazal Rendez-Vous"

User = collections.namedtuple("User", "pid name password")

users = [
	User(2, "Quazal Rendez-Vous", "password"),
	User(100, "guest", "MMQea3n!fsik")
]

def get_user_by_name(name):
	for user in users:
		if user.name == name:
			return user

server = get_user_by_name(SECURE_SERVER)

url = common.StationURL(
	scheme="prudps", address="127.0.0.1", port=1224,
	PID = server.pid, CID = 1, type = 2,
    sid = 1, stream = 10
)

print(url)