class ByteFIFO(object):
    def __init__(self):
        self._buf = bytearray()

    def put(self, data):
        self._buf.extend(data)

    def get(self, size):
        data = self._buf[:size]
        self._buf[:size] = b''
        return data

    def peek(self, size):
        return self._buf[:size]
    
    def clear(self):
        self._buf = bytearray()

    def __len__(self):
        return len(self._buf)
