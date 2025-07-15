from nintendo.nex import settings, rmc


if __name__ == "__main__":
    s = settings.default()
    msg = rmc.RMCMessage(s)

    msg.mode = msg.REQUEST
    msg.protocol = 1
    msg.call_id = 42
    msg.method = 123
    msg.body = b"Hello, world!"

    encoded_data = msg.encode()
    print(f"Encoded data: {encoded_data.hex()}")

    decoded_msg = rmc.RMCMessage(s)
    decoded_msg.decode(encoded_data)

    print("Decoded data:")
    print("Protocol:", decoded_msg.protocol)
    print("Mode:", "REQUEST" if decoded_msg.mode == decoded_msg.REQUEST else "RESPONSE")
    print("Call ID:", decoded_msg.call_id)
    print("Method:", decoded_msg.method)
    print("Body:", decoded_msg.body)
  
