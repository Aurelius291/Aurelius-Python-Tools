import asyncio
import tracemalloc
import io

from protocol import RespParser, encode_resp
from store import Store

tracemalloc.start(25) 

class RedPyServer:
    def __init__(self):
        self.store = Store()
        self.expiry = {}

    def execute(self, cmd):
        if not isinstance(cmd, list) or len(cmd) == 0:
            return "-ERR protocol error\r\n"
        
        cmd_name = cmd[0]
        
        if isinstance(cmd_name, bytes):
            cmd_name = cmd_name.decode()
        cmd_name = cmd_name.upper()

        args = cmd[1:]
        return self.store.execute_command(cmd_name, *args)

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(4096)
            if not data:
                break

            stream = io.BytesIO(data)
            parser = RespParser(stream)
            
            try:
                while True:
                    cmd = parser.parse()

                    reply = self.execute(cmd)
                    writer.write(encode_resp(reply))

            except Exception:
                pass

            await writer.drain()
    
    async def start(self, host="127.0.0.1", port=6379):
        server = await asyncio.start_server(
            self.handle_client, host, port
        )
        async with server:
            await server.serve_forever()

def main():
    server = RedPyServer()

    asyncio.run(server.start())

if __name__ == "__main__":
    main()