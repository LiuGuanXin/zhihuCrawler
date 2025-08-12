import asyncio
import json

from util.tools import parse_cookies
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher, \
    JsonCssExtractionStrategy

from zhihu import schema
from zhihu.schema import question_schema

# 原始 cookie（注意：是字符串，不是列表）
raw_cookie_str = "_zap=967bd34b-6202-4cfa-a399-7b30c44b7d25; d_c0=AEASPmevRBmPTsby-JGDk-gVchbjWeGcC7E=|1726886113; __snaker__id=yorOpGJsf8k6WMe7; q_c1=24c8548255db4895819cc344d492d6ac|1726886168000|1726886168000; _xsrf=Hh7YbvfjDYDmvybJ4wDnmRx3HYZOLGZg; edu_user_uuid=edu-v1|8cfd1695-13a4-479b-90a6-f6d2a33b2634; ff_supports_webp=1; __zse_ck=004_sEmKemDdDpdIGvNpTUimVWiFCLtd2OZt6a5xYQHKp8gXdaxjgHs9MlJZp0qCii4sXwLghrQhklJKSnzWmtCj0eoBDZDJE7cSnST1AdCTYQZ9gxJrKfH3TYw2EWhBoRm/-lNRFx3K3z7AW2B+JHkRZSy6oDrNhgcpRr+Sk3gsIVHkuPGPc0a0W/JtAwBzII7DmCTcKw4qxmRgwcPpKp3i6FBcTAVEjmpYrPA7iu4EHZwzoUkECuZUTjusdSgAqOlw2; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1754040121,1754265893,1754299512,1754353454; HMACCOUNT=17D799FEB93ECC0D; tst=h; SESSIONID=rGSOIlog1v64K2iEJZgHfw4fkepRffBE5s6ykNDkAg1; JOID=WlAcB0P3rR1jxL87Y3C9iMZZuqp4hetDII3TVQnG2ypag41SJ0rLjQfEvjdiHKtZAvkcjdx2urQub5ufZRpLXy8=; osd=VlAWAkv7rRdmzLM7aXW1hMZTv6J0heFGKIHTXwzO1ypQhoVeJ0DOhQvEtDJqEKtTB_EQjdZzsrguZZ6XaRpBWic=; gdxidpyhxdE=%2B8tuV1kfE1tjdZzff%2FH0s%5CyMHxQ%5Cy%2BKaq20jLbcLfMM89Cv4eVi16OOaOh0Wg51CvtVqzMYPyZrZ%5CbmZEwRxrSGtlPw6LVRsENVBmUMtA7BBnjZd2sC%2BA7vzjmSDq8VyP3gX3zkGfHUfnmYmufCH5fM2PXOEitHnk7d46kWm%5CkvIrMoS%3A1754363037018; DATE=1754362145667; cmci9xde=U2FsdGVkX1811Etom8faicNSHYeWi07mLLwhnf+5iIrSDygJZweSMeP41QF+XfsVsQh8oXxjlr2IkCvWIlvk3Q==; pmck9xge=U2FsdGVkX1+fQcJckMwwOE+UX60JvzCPQc8hg2fnjzw=; assva6=U2FsdGVkX19all9gV4JxxnNiyYclXd9xeiK849/DirM=; assva5=U2FsdGVkX185udk0ys1sVCy/w2rzrP/04rTpQEoB/D+2gzc/KnDpEr6bUsfCa30qvqP4F2BTTymbUeBIWoQsUA==; crystal=U2FsdGVkX19ws9U4RWRzPceYJayq1l8ccn5WYqV18YAX7m4gTOaO7dwZz302O8Y7jxaMYkxZ3bVJizfNgNlSNTI3OS20gDPmlmL001dNB1Gd0KNPuavieomGhP3Fo2DojTrmvJffKXgiBocWxmysRsDHCydOeFKVFwfu/ni4h913phDz4Yx+QLgtiCSGoFQp0OVgRlDOxS0uzdYtqil0aotWAHb6fGQ+RyC8x1oHh9FMV4okq3OYJJVJEPgbYmFH; vmce9xdq=U2FsdGVkX1/OnC9TpBVPHLZlJiD3XO9XYx70v09kM/+62GEQJI9n16l2MchygSh4yaH4t98haUaWvYmeXNddMa+F7jaeP+FeU845i0TgzISrMCMb4d/RCEgsPz9wKwQS3OuPCnnPgSN50G/TUgUb0XYimRkJehOy45c0nCNdmDQ=; captcha_session_v2=2|1:0|10:1754362207|18:captcha_session_v2|88:ZDBCdnNmUWhpNmpjb0tvYXFNQ1VoRTlDaThPZUlxZzdXMDl0cHdxQ1VsLytLbVhpWWpyYTU1OXB1dWdoaHdEQw==|d792a9162654c9ffcf4ef2a26659781ccd0981d8ea59792b8ff320d52ff2aa5b; z_c0=2|1:0|10:1754362229|4:z_c0|92:Mi4xVEZWd0FnQUFBQUFBUUJJLVo2OUVHU1lBQUFCZ0FsVk5jNzktYVFBNTJhdXhDZXFfWWVDMl9PelJJblF3Y1lvME5n|a9bb830088ef3d6b7029b92dcd4794ef8b0a6d24de0e78db4a083bd396ec7a1e; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1754363420; BEC=6ff32b60f55255af78892ba1e551063a"

async def main():
    # Configure the browser
    browser_cfg = BrowserConfig(
        verbose=True,
        # headless=False,
        browser_type="chromium",
        cookies=parse_cookies(raw_cookie_str)
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(question_schema),
        stream=False
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
    )

    async with AsyncWebCrawler(browser_cfg=browser_cfg) as crawler:
        results = await crawler.arun_many(
            urls=["https://www.zhihu.com/question/1936518114176103800",
                  "https://www.zhihu.com/question/20120168"],
            config=run_config,
            dispatcher=dispatcher
        )
        # Process all results after completion
        for result in results:
            if result.success and result.extracted_content:
                result_json = json.loads(result.extracted_content)
                print(result_json)
            if result.success:
                # Different content formats
                print(result.html)         # Raw HTML
                print(result.cleaned_html) # Cleaned HTML
                print(result.markdown.raw_markdown) # Raw markdown from cleaned html
                print(result.markdown.fit_markdown) # Most relevant content in markdown

                # Check success status
                print(result.success)      # True if crawl succeeded
                print(result.status_code)  # HTTP status code (e.g., 200, 404)

                # Access extracted media and links
                print(result.media)        # Dictionary of found media (images, videos, audio)
                print(result.links)        # Dictionary of internal and external links
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
