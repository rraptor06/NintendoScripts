from nintendo.nex import prudp, settings


if __name__ == "__main__":
    s = settings.default()
    pkt = prudp.PRUDPPacket()
    pkt.source_type = 1
    pkt.source_port = 0
    pkt.dest_type = 2
    pkt.dest_port = 0
    pkt.type = 0
    pkt.flags = 1
    pkt.signature = b"\x00" * 16
    pkt.connection_signature = b"\x00\x00\x00\x00"
    pkt.payload = b""

    pkt_v0 = prudp.PRUDPMessageV0(s)
    encoded_v0 = pkt_v0.encode(pkt)

    print(f"Encoded Packet V0 Bytes: {encoded_v0}")
    print(f"Encoded Packet V0 Hex: {encoded_v0.hex()}")

    pkt_v1 = prudp.PRUDPMessageV1(s)
    encoded_v1 = pkt_v1.encode(pkt)

    print(f"Encoded Packet V1 Bytes: {encoded_v1}")
    print(f"Encoded Packet V1 Hex: {encoded_v1.hex()}")

    pkt_lite = prudp.PRUDPLiteMessage(s)
    encoded_lite = pkt_lite.encode(pkt)

    print(f"Encoded Packet Lite Bytes: {encoded_lite}")
    print(f"Encoded Packet Lite Hex: {encoded_lite.hex()}")
