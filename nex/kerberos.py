import hashlib
import hmac
from Crypto.Cipher import ARC4
from datetime import datetime, timedelta

# Données du ticket fournies dans l'exercice (concaténation des lignes pour simplification)
ticket_hex = (
    "86e5b91add71b984c713dab188cdcabc1b4298f922021fe4be049be91b279489"
    "0de22074734bfd9e75ac3f4ecbb31155933845c601dc8b45d5c7f8e055d80a3c"
    "cef3ee876cbc64c4a7802f20c126be6c73398d367c934902b7cfe7a187d1d38e"
    "6bfe18c564217c53a01f11002b19cf7c5361ffb65ba10fe87e0cc8005a1a674a"
    "fd7461c5154b193a62ccaad8e1a9a28d92645e69"
)

# Paramètres
guest_pid = 564330319085596911
guest_password = "MMQea3n!fsik"
quazal_rdv_pid = 257049437023956657
quazal_rdv_password = "5MYiXWwtBuI6JzhU"

# Conversion hexadécimale vers octets
ticket_bytes = bytes.fromhex(ticket_hex)

# Séparation ticket + HMAC-MD5 (derniers 16 octets)
ticket_data = ticket_bytes[:-16]
ticket_hmac = ticket_bytes[-16:]

# Fonction pour générer la clé depuis mot de passe (Switch)
def derive_key(password: str, pid: int) -> bytes:
    pwd_md5 = hashlib.md5(password.encode()).digest()
    pid_bytes = pid.to_bytes(8, byteorder='little')
    return hashlib.md5(pwd_md5 + pid_bytes).digest()

# Vérification HMAC
def verify_hmac(data: bytes, expected_hmac: bytes, key: bytes) -> bool:
    computed = hmac.new(key, data, hashlib.md5).digest()
    return computed == expected_hmac

# Décryptage RC4
def decrypt_rc4(data: bytes, key: bytes) -> bytes:
    cipher = ARC4.new(key)
    return cipher.decrypt(data)

# Étapes :
# 1. Clé source = dérivée du mot de passe du guest
source_key = derive_key(guest_password, guest_pid)

# 2. Vérification du HMAC
hmac_valid = verify_hmac(ticket_data, ticket_hmac, source_key)

# 3. Décryptage du ticket principal
decrypted_ticket = decrypt_rc4(ticket_data, source_key)

# 4. Lecture du contenu du ticket déchiffré
session_key = decrypted_ticket[:32]
target_pid = int.from_bytes(decrypted_ticket[32:40], byteorder='little')
internal_ticket = decrypted_ticket[40:]

# 5. Déchiffrement du ticket interne (nouveau format)
random_key = internal_ticket[:16]
enc_ticket_info = internal_ticket[16:]

# Clé cible = dérivée du mot de passe Quazal Rendez-Vous + random key
target_key = derive_key(quazal_rdv_password, quazal_rdv_pid)
final_key = hashlib.md5(target_key + random_key).digest()

# Déchiffrement du ticket interne
decrypted_internal = decrypt_rc4(enc_ticket_info, final_key)

# Lecture : DateTime (8 bytes), PID (8 bytes), session key (32 bytes)
issued_timestamp = int.from_bytes(decrypted_internal[:8], byteorder='little')
source_pid = int.from_bytes(decrypted_internal[8:16], byteorder='little')
session_key_check = decrypted_internal[16:48]

# Conversion du timestamp (Windows FILETIME)
windows_epoch = datetime(1601, 1, 1)
issued_time = windows_epoch + timedelta(microseconds=issued_timestamp // 10)

# Résultat
{
    "hmac_valid": hmac_valid,
    "session_key": session_key.hex(),
    "target_pid": target_pid,
    "internal_ticket_decrypted": {
        "source_pid": source_pid,
        "session_key_internal": session_key_check.hex(),
        "timestamp": issued_time.isoformat()
    }
}
