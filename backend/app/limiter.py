from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

def get_real_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)
```

And in Render backend → **Environment**, add:
```
FORWARDED_ALLOW_IPS=*
