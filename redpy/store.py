from commands import Commands

class Store(Commands):
    def __init__(self):
        self.store = {}
        self.expiry = {}

    def execute_command(self, name, *args, keys=None):
        cmd_name = name.decode() if isinstance(name, bytes) else str(name)
        cmd_name = cmd_name.upper()
        args = tuple(a.decode() if isinstance(a, bytes) else a for a in args)

        handler = getattr(self, f"_{cmd_name.lower()}", None)
        if handler is None:
            return f"-ERR unknown command '{cmd_name}'"
        return handler(*args)

    def _get(self, key):
        val = self.store.get(key)
        if val is None:
            return None
        return val.encode() if isinstance(val, str) else val

    def _set(self, key, value):
        self.store[key] = value
        return "OK"
    
    def _del(self, key):
        deleted = {}
        dicts = self.store[key]
        deleted[dicts]
        return deleted