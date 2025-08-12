import http.cookies

def parse_cookies(cookie_str, domain=".zhihu.com", path="/"):
    parsed_cookies = []
    cookie_parser = http.cookies.SimpleCookie()
    cookie_parser.load(cookie_str)

    for key, morsel in cookie_parser.items():
        cookie = {
            "name": key,
            "value": morsel.value,
            "domain": domain,
            "path": path,
            # 可选：设置 secure / httpOnly
            # "secure": True,
            # "httpOnly": True,
        }
        parsed_cookies.append(cookie)

    return parsed_cookies


