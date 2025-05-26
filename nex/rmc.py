import struct

class RMCRequest:
    def __init__(self, protocol_id, call_id, method_id, parameters=b'', extended_protocol_id=None):
        self.protocol_id = protocol_id
        self.call_id = call_id
        self.method_id = method_id
        self.parameters = parameters
        self.extended_protocol_id = extended_protocol_id

    def build(self):
        data = b''
        proto = self.protocol_id | 0x80

        # Header
        data += struct.pack('<B', proto)
        if self.protocol_id == 0x7F:
            if self.extended_protocol_id is None:
                raise ValueError("Extended protocol ID is required for protocol ID 0x7F")
            data += struct.pack('<H', self.extended_protocol_id)

        data += struct.pack('<I', self.call_id)
        data += struct.pack('<I', self.method_id)
        data += self.parameters

        # Size = total size minus 4 bytes (size field itself)
        size = len(data)
        return struct.pack('<I', size) + data

    @staticmethod
    def parse(raw):
        size = struct.unpack_from('<I', raw, 0)[0]
        offset = 4
        protocol_id = raw[offset]
        offset += 1

        extended_protocol_id = None
        if protocol_id == 0xFF:
            extended_protocol_id = struct.unpack_from('<H', raw, offset)[0]
            offset += 2

        call_id = struct.unpack_from('<I', raw, offset)[0]
        offset += 4
        method_id = struct.unpack_from('<I', raw, offset)[0]
        offset += 4
        parameters = raw[offset:]

        return {
            'size': size,
            'protocol_id': protocol_id & 0x7F,
            'extended_protocol_id': extended_protocol_id,
            'call_id': call_id,
            'method_id': method_id,
            'parameters': parameters
        }


class RMCResponse:
    def __init__(self, protocol_id, success, call_id, method_id=None, response_data=b'', error_code=None, extended_protocol_id=None):
        self.protocol_id = protocol_id
        self.success = success
        self.call_id = call_id
        self.method_id = method_id
        self.response_data = response_data
        self.error_code = error_code
        self.extended_protocol_id = extended_protocol_id

    def build(self):
        data = b''
        data += struct.pack('<B', self.protocol_id)
        if self.protocol_id == 0x7F:
            if self.extended_protocol_id is None:
                raise ValueError("Extended protocol ID is required for protocol ID 0x7F")
            data += struct.pack('<H', self.extended_protocol_id)

        data += struct.pack('<B', 1 if self.success else 0)

        if self.success:
            data += struct.pack('<I', self.call_id)
            data += struct.pack('<I', self.method_id | 0x8000)
            data += self.response_data
        else:
            data += struct.pack('<I', self.error_code)
            data += struct.pack('<I', self.call_id)

        size = len(data)
        return struct.pack('<I', size) + data

    @staticmethod
    def parse(raw):
        size = struct.unpack_from('<I', raw, 0)[0]
        offset = 4
        protocol_id = raw[offset]
        offset += 1

        extended_protocol_id = None
        if protocol_id == 0x7F:
            extended_protocol_id = struct.unpack_from('<H', raw, offset)[0]
            offset += 2

        success = bool(raw[offset])
        offset += 1

        if success:
            call_id = struct.unpack_from('<I', raw, offset)[0]
            offset += 4
            method_id = struct.unpack_from('<I', raw, offset)[0] & ~0x8000
            offset += 4
            response_data = raw[offset:]
            return {
                'success': True,
                'protocol_id': protocol_id,
                'extended_protocol_id': extended_protocol_id,
                'call_id': call_id,
                'method_id': method_id,
                'response_data': response_data
            }
        else:
            error_code = struct.unpack_from('<I', raw, offset)[0]
            offset += 4
            call_id = struct.unpack_from('<I', raw, offset)[0]
            return {
                'success': False,
                'protocol_id': protocol_id,
                'extended_protocol_id': extended_protocol_id,
                'error_code': error_code,
                'call_id': call_id
            }
