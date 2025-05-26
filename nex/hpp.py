import hashlib
import hmac
import requests
from Crypto.Cipher import ARC4

# ==== Paramètres de la requête ====
game_server_id = "0008c500"  # Exemple : Tomodachi Life
environment = "L1"           # Environnement, ex: L1, C1, etc.
nex_version = "NEX_2_4_1_S25"
pid = 123456789              # Remplace par l'identifiant du joueur
access_key = b"yourAccessKey"  # Clé d'accès du serveur (ex. de la rom)
password = "userPassword"      # Mot de passe du compte

# ==== Construction de l'URL ====
url = f"https://hpp-{game_server_id}-{environment}.n.app.nintendo.net/hpp/"

# ==== Corps de la requête ====
# Ceci est un exemple. Le vrai contenu dépend de la méthode appelée (binaire généralement)
request_body = b"\x00\x01\x02\x03\x04"

# ==== Génération des signatures ====

# --- Signature1 (clé d'accès, 8 octets)
key1 = access_key.ljust(8, b'\x00')  # Padding avec des zéros
signature1 = hmac.new(key1, request_body, hashlib.md5).hexdigest()

# --- Signature2 (dérivation type Kerberos + HMAC-MD5)
def derive_password_key(password: str) -> bytes:
    # Dérivation de la clé depuis le mot de passe (Kerberos)
    pw_hash = hashlib.md5(password.encode('utf-8')).digest()
    cipher = ARC4.new(pw_hash)
    return cipher.encrypt(b"\x00" * 16)

key2 = derive_password_key(password)
signature2 = hmac.new(key2, request_body, hashlib.md5).hexdigest()

# ==== En-têtes HTTP ====
headers = {
    "pid": str(pid),
    "version": nex_version,
    "token": "normaltoken",
    "signature1": signature1,
    "signature2": signature2,
    "Content-Type": "application/octet-stream",
    "User-Agent": "HPPClient/1.0"
}

# ==== Envoi de la requête ====
try:
    response = requests.post(url, headers=headers, data=request_body)
    print(f"Status code: {response.status_code}")
    print(f"Response (hex): {response.content.hex()}")
except Exception as e:
    print(f"Error during request: {e}")
