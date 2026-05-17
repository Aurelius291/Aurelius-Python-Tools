from datetime import datetime

class Commands:
    def get(self, key):
        return self.execute_command("GET", key, keys=[key])
    
    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        args = [key, value]

        if ex is not None:
            args.extend(["EX", str(ex)])
        elif px is not None:
            args.extend(["PX", str(px)])
            
        if nx:
            args.append("NX")
        elif xx:
            args.append("XX")
        return self.execute_command("SET", *args, keys=[key])
    
    def delete(self, *key):
        return self.execute_command("DEL", *key)
    
    def expire(self, key, time, gt=False, lt=False, nx= False, xx=False):
        """
        Valid options are:
            NX -> Set expiry only when the key has no expiry
            XX -> Set expiry only when the key has an existing expiry
            GT -> Set expiry only when the new expiry is greater than current one
            LT -> Set expiry only when the new expiry is less than current one
        """
        if isinstance(time, datetime.timedelta):
            time = int(time.total_seconds())

        exp_option = list()
        if nx:
            exp_option.append("NX")
        if xx:
            exp_option.append("XX")
        if gt:
            exp_option.append("GT")
        if lt:
            exp_option.append("LT")

        return self.execute_command("EXPIRE", key, time, *exp_option)
    
    def append(self, key, value):
        return self.execute_command("APPEND", key, value)
    
    def hello(self): # Redis docs says intentially throws error
        raise NotImplementedError( "HELLO is intentionally not implemented in the client.")
    
    def ttl(self, key):
        """
        Returns the number of seconds until the key ``key`` will expire
        """
        return self.execute_command("TTL", key)

    def quit(self, *kwargs):
        return self.execute_command("QUIT", **kwargs)