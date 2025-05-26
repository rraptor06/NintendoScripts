import struct
import hashlib
import hmac

# Constantes pour les types de paquets
PRUDP_TYPE_SYN = 0
PRUDP_TYPE_CONNECT = 1
PRUDP_TYPE_DATA = 2
PRUDP_TYPE_DISCONNECT = 3
PRUDP_TYPE_PING = 4
PRUDP_TYPE_USER = 5

# Drapeaux
FLAG_ACK = 0x001
FLAG_RELIABLE = 0x002
FLAG_NEED_ACK = 0x004
FLAG_HAS_SIZE = 0x008
FLAG_MULTI_ACK = 0x200

# Clé d'accès (exemple)
ACCESS_KEY = b'ridfebb9'

def md5(data):
    return hashlib.md5(data).digest()

def hmac_md5(key, data):
    return hmac.new(key, data, hashlib.md5).digest()

def calc_checksum(data):
    # Calcule la somme de contrôle sur l'ensemble du paquet
    words = struct.unpack_from("<%iI" % (len(data) // 4), data)
    temp = sum(words) & 0xFFFFFFFF  # 32 bits

    checksum = sum(ACCESS_KEY)
    checksum += sum(data[len(data) & ~3:])
    checksum += sum(struct.pack("I", temp))
    return checksum & 0xFF  # 8 bits

class PRUDPPacketV0:
    def __init__(self, source, destination, type_flags, session_id, sequence_id, payload=b'', fragment_id=0, connection_signature=b'\x00\x00\x00\x00'):
        self.source = source
        self.destination = destination
        self.type_flags = type_flags
        self.session_id = session_id
        self.sequence_id = sequence_id
        self.payload = payload
        self.fragment_id = fragment_id
        self.connection_signature = connection_signature

    def build(self):
        header = struct.pack('<BBH', self.source, self.destination, self.type_flags)
        header += struct.pack('<B', self.session_id)

        # Signature du paquet
        if self.type_flags >> 4 == PRUDP_TYPE_DATA and not self.payload:
            signature = b'\x78\x56\x34\x12'
        elif self.type_flags >> 4 in (PRUDP_TYPE_DATA, PRUDP_TYPE_DISCONNECT):
            key = md5(ACCESS_KEY)
            data = struct.pack('<H', self.sequence_id) + struct.pack('<B', self.fragment_id) + self.payload
            signature = hmac_md5(key, data)[:4]
        else:
            signature = self.connection_signature

        header += signature
        header += struct.pack('<H', self.sequence_id)

        # Données spécifiques au paquet
        packet_specific = b''
        if self.type_flags >> 4 in (PRUDP_TYPE_SYN, PRUDP_TYPE_CONNECT):
            packet_specific += self.connection_signature
        elif self.type_flags >> 4 == PRUDP_TYPE_DATA:
            packet_specific += struct.pack('<B', self.fragment_id)
        if self.type_flags & FLAG_HAS_SIZE:
            packet_specific += struct.pack('<H', len(self.payload))

        packet = header + packet_specific + self.payload
        checksum = calc_checksum(packet)
        packet += struct.pack('<B', checksum)
        return packet

class PRUDPPacketV1:
    def __init__(self, source, destination, type_flags, session_id, substream_id, sequence_id, payload=b'', session_key=b'', connection_signature=b''):
        self.source = source
        self.destination = destination
        self.type_flags = type_flags
        self.session_id = session_id
        self.substream_id = substream_id
        self.sequence_id = sequence_id
        self.payload = payload
        self.session_key = session_key
        self.connection_signature = connection_signature

    def build(self):
        magic = b'\xEA\xD0'
        packet_specific_data = b''  # À remplir selon les besoins
        payload_size = len(self.payload)
        header = struct.pack('<BBHBBHBBH',
                             1,  # Version PRUDP
                             len(packet_specific_data),
                             payload_size,
                             self.source,
                             self.destination,
                             self.type_flags,
                             self.session_id,
                             self.substream_id,
                             self.sequence_id)

        # Signature du paquet
        key = md5(ACCESS_KEY)
        data = header[4:] + self.session_key + struct.pack('<I', sum(ACCESS_KEY)) + self.connection_signature + packet_specific_data + self.payload
        signature = hmac_md5(key, data)

        packet = magic + header + signature + packet_specific_data + self.payload
        return packet

class PRUDPPacketLite:
    def __init__(self, source_type, destination_type, source_port, destination_port, type_flags, sequence_id, payload=b'', fragment_id=0, packet_specific_data=b''):
        self.source_type = source_type
        self.destination_type = destination_type
        self.source_port = source_port
        self.destination_port = destination_port
        self.type_flags = type_flags
        self.sequence_id = sequence_id
        self.payload = payload
        self.fragment_id = fragment_id
        self.packet_specific_data = packet_specific_data

    def build(self):
        magic = b'\x80'
        payload_size = len(self.payload)
        header = struct.pack('<BBHBBB',
                             len(self.packet_specific_data),
                             payload_size,
                             (self.source_type << 4) | self.destination_type,
                             self.source_port,
                             self.destination_port,
                             self.fragment_id)
        header += struct.pack('<H', self.type_flags)
        header += struct.pack('<H', self.sequence_id)

        packet = magic + header + self.packet_specific_data + self.payload
        return packet

# Exemple d'utilisation
if __name__ == "__main__":
    # Paquet V0
    packet_v0 = PRUDPPacketV0(
        source=0x01,
        destination=0x02,
        type_flags=(FLAG_RELIABLE << 4) | PRUDP_TYPE_DATA,
        session_id=0x01,
        sequence_id=0x0001,
        payload=b'Hello, PRUDP V0!',
        fragment_id=0,
        connection_signature=b'\x00\x00\x00\x00'
    )
    data_v0 = packet_v0.build()
    print(f"Paquet V0: {data_v0.hex()}")

    # Paquet V1
    packet_v1 = PRUDPPacketV1(
        source=0x01,
        destination=0x02,
        type_flags=(FLAG_RELIABLE << 4) | PRUDP_TYPE_DATA,
        session_id=0x01,
        substream_id=0x00,
        sequence_id=0x0001,
        payload=b'Hello, PRUDP V1!',
        session_key=b'',
        connection_signature=b''
    )
    data_v1 = packet_v1.build()
    print(f"Paquet V1: {data_v1.hex()}")

    # Paquet Lite
    packet_lite = PRUDPPacketLite(
        source_type=0xA,
        destination_type=0xA,
        source_port=0x01,
        destination_port=0x01,
        type_flags=(FLAG_RELIABLE << 4) | PRUDP_TYPE_DATA,
        sequence_id=0x0001,
        payload=b'Hello, PRUDP Lite!',
        fragment_id=0,
        packet_specific_data=b''
    )
    data_lite = packet_lite.build()
    print(f"Paquet Lite: {data_lite.hex()}")
