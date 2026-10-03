"""URL policy only; deployment ingress must provide actual TLS."""
import argparse
from urllib.parse import urlsplit

def transit_ok(url: str, allow_localhost: bool = False) -> bool:
    try:
        u = urlsplit(url)
        _ = u.port
        if not u.hostname or u.username or u.password or u.fragment:
            return False
        return u.scheme == 'https' or (allow_localhost and u.scheme == 'http' and u.hostname in {'localhost','127.0.0.1','::1'})
    except ValueError:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url'); parser.add_argument('--lab', action='store_true')
    args = parser.parse_args()
    print('PASS' if transit_ok(args.url, args.lab) else 'DENIED')
    raise SystemExit(0 if transit_ok(args.url, args.lab) else 1)
