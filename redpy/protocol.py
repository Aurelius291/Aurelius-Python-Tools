import io

class RedPyError(Exception):
    """
    Raised when RedPy results with an error;
    when the prefix is like "ERR" or "WRONGTYPE".
    """

class MovedError(Exception):
    """
    Raised when cluster redirects
    """

class RespParser:
    def __init__(self, stream):
        self.stream = stream
    
    def parse(self):
        line = self.stream.readline()
        if not line:
            raise EOFError
        
        prefix = chr(line[0])
        payload = line[1:].rstrip(b"\r\n").decode()

        dispatch = {
            "+": self._simple_string,
            "-": self._error,
            ":": self._integer,
            "$": self._bulk_string,
            "*": self._array,
        }

        handler = dispatch.get(prefix)
        if not handler:
            raise ValueError(f"Unknown RESP type byte: {prefix!r}")
        return handler(payload)
    
    def _simple_string(self, data):
        return data
    
    def _error(self, data):
        parts = data.split(" ", 1)
        code = parts[0]
        message = parts[1] if len(parts) > 1 else ""
        if code == "MOVED":
            slot, addr = message.split(" ")
            raise MovedError(int(slot), addr)
        raise RedPyError(data)
    
    def _integer(self, data):
        return int(data)
    
    def _bulk_string(self, data):
        length = int(data)
        if length == -1:
            return None
        value = self.stream.read(length)
        self.stream.read(2)
        return value
    
    def _array(self, data):
        count = int(data)
        if count == -1:
            return None
        return [self.parse() for _ in range(count)]

def encode_resp(value):
    if value is None:
        return b"$-1\r\n"
    elif isinstance(value, str):
        return f"+{value}\r\n".encode()
    elif isinstance(value, int):
        return f":{value}\r\n".encode()
    elif isinstance(value, bytes):
        return f"${len(value)}\r\n".encode() + value + b"\r\n"
    elif isinstance(value, list):
        out = f"*{len(value)}\r\n".encode()
        for item in value:
            out += encode_resp(item)
        return out
    elif isinstance(value, Exception):
        return f"-ERR {value}\r\n".encode()

def make_parser(raw: str):
    return RespParser(io.BytesIO(raw.encode()))

assert make_parser("+OK\r\n").parse() == "OK"
assert make_parser(":100\r\n").parse() == 100
assert make_parser("$3\r\nfoo\r\n").parse() == b"foo"
assert make_parser("$-1\r\n").parse() is None
assert make_parser("*2\r\n+hello\r\n:42\r\n").parse() == ["hello", 42]

try:
    make_parser("-ERR something went wrong\r\n").parse()
except RedPyError as e:
    assert "something went wrong" in str(e)