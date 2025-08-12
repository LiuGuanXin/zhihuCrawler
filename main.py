import os
import json
import logging
from datetime import datetime
from typing import List

from zhihu.ZhihuCrawler import ZhihuCrawler

# 知乎的cookie，登陆后从浏览器获取
raw_cookie_str = "ASPmevRBmPTsby-JGDk-gVchbjWeGcC7E=|1726886113; __snaker__id=yorOpGJsf8k6WMe7; q_c1=24c8548255db4895819cc344d492d6ac|1726886168000|1726886168000; _xsrf=Hh7YbvfjDYDmvybJ4wDnmRx3HYZOLGZg; edu_user_uuid=edu-v1|8cfd1695-13a4-479b-90a6-f6d2a33b2634; ff_supports_webp=1; __zse_ck=004_sEmKemDdDpdIGvNpTUimVWiFCLtd2OZt6a5xYQHKp8gXdaxjgHs9MlJZp0qCii4sXwLghrQhklJKSnzWmtCj0eoBDZDJE7cSnST1AdCTYQZ9gxJrKfH3TYw2EWhBoRm/-lNRFx3K3z7AW2B+JHkRZSy6oDrNhgcpRr+Sk3gsIVHkuPGPc0a0W/JtAwBzII7DmCTcKw4qxmRgwcPpKp3i6FBcTAVEjmpYrPA7iu4EHZwzoUkECuZUTjusdSgAqOlw2; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1754040121,1754265893,1754299512,1754353454; HMACCOUNT=17D799FEB93ECC0D; tst=h; SESSIONID=rGSOIlog1v64K2iEJZgHfw4fkepRffBE5s6ykNDkAg1; JOID=WlAcB0P3rR1jxL87Y3C9iMZZuqp4hetDII3TVQnG2ypag41SJ0rLjQfEvjdiHKtZAvkcjdx2urQub5ufZRpLXy8=; osd=VlAWAkv7rRdmzLM7aXW1hMZTv6J0heFGKIHTXwzO1ypQhoVeJ0DOhQvEtDJqEKtTB_EQjdZzsrguZZ6XaRpBWic=; gdxidpyhxdE=%2B8tuV1kfE1tjdZzff%2FH0s%5CyMHxQ%5Cy%2BKaq20jLbcLfMM89Cv4eVi16OOaOh0Wg51CvtVqzMYPyZrZ%5CbmZEwRxrSGtlPw6LVRsENVBmUMtA7BBnjZd2sC%2BA7vzjmSDq8VyP3gX3zkGfHUfnmYmufCH5fM2PXOEitHnk7d46kWm%5CkvIrMoS%3A1754363037018; DATE=1754362145667; cmci9xde=U2FsdGVkX1811Etom8faicNSHYeWi07mLLwhnf+5iIrSDygJZweSMeP41QF+XfsVsQh8oXxjlr2IkCvWIlvk3Q==; pmck9xge=U2FsdGVkX1+fQcJckMwwOE+UX60JvzCPQc8hg2fnjzw=; assva6=U2FsdGVkX19all9gV4JxxnNiyYclXd9xeiK849/DirM=; assva5=U2FsdGVkX185udk0ys1sVCy/w2rzrP/04rTpQEoB/D+2gzc/KnDpEr6bUsfCa30qvqP4F2BTTymbUeBIWoQsUA==; crystal=U2FsdGVkX19ws9U4RWRzPceYJayq1l8ccn5WYqV18YAX7m4gTOaO7dwZz302O8Y7jxaMYkxZ3bVJizfNgNlSNTI3OS20gDPmlmL001dNB1Gd0KNPuavieomGhP3Fo2DojTrmvJffKXgiBocWxmysRsDHCydOeFKVFwfu/ni4h913phDz4Yx+QLgtiCSGoFQp0OVgRlDOxS0uzdYtqil0aotWAHb6fGQ+RyC8x1oHh9FMV4okq3OYJJVJEPgbYmFH; vmce9xdq=U2FsdGVkX1/OnC9TpBVPHLZlJiD3XO9XYx70v09kM/+62GEQJI9n16l2MchygSh4yaH4t98haUaWvYmeXNddMa+F7jaeP+FeU845i0TgzISrMCMb4d/RCEgsPz9wKwQS3OuPCnnPgSN50G/TUgUb0XYimRkJehOy45c0nCNdmDQ=; captcha_session_v2=2|1:0|10:1754362207|18:captcha_session_v2|88:ZDBCdnNmUWhpNmpjb0tvYXFNQ1VoRTlDaThPZUlxZzdXMDl0cHdxQ1VsLytLbVhpWWpyYTU1OXB1dWdoaHdEQw==|d792a9162654c9ffcf4ef2a26659781ccd0981d8ea59792b8ff320d52ff2aa5b; z_c0=2|1:0|10:1754362229|4:z_c0|92:Mi4xVEZWd0FnQUFBQUFBUUJJLVo2OUVHU1lBQUFCZ0FsVk5jNzktYVFBNTJhdXhDZXFfWWVDMl9PelJJblF3Y1lvME5n|a9bb830088ef3d6b7029b92dcd4794ef8b0a6d24de0e78db4a083bd396ec7a1e; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1754363420; BEC=6ff32b60f55255af78892ba1e551063a"

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def question_urls(hot_json: json):
    """生成知乎问题详情 URL 列表"""
    urls: List[str] = [
        item["url"] for item in hot_json if item.get("url")
    ]
    return urls

def author_urls(author_json: json):
    """生成用户详情 URL 列表"""
    urls = []
    for key, value in author_json.items():
        for v in value:
            if v.get('author_url'):
                urls.append(v['author_url'])
    return urls

def save_json(question_json, hot_json, author_json):
    # === 文件保存部分 ===
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    save_dir = os.path.join("output", timestamp)
    os.makedirs(save_dir, exist_ok=True)  # 确保目录存在

    # 保存 hot_json
    hot_file = os.path.join(save_dir, "hot_list.json")
    with open(hot_file, "w", encoding="utf-8") as f:
        json.dump(hot_json, f, ensure_ascii=False, indent=2)
    logger.info(f"Hot list saved to {hot_file}")

    # 保存 question details
    detail_file = os.path.join(save_dir, "question_details.json")
    with open(detail_file, "w", encoding="utf-8") as f:
        json.dump(question_json, f, ensure_ascii=False, indent=2)
    logger.info(f"Question details saved to {detail_file}")

    # 保存 author details
    author_file = os.path.join(save_dir, "author_json.json")
    with open(author_file, "w", encoding="utf-8") as f:
        json.dump(author_json, f, ensure_ascii=False, indent=2)
    logger.info(f"Author details saved to {author_file}")


async def main():
    """主函数，执行知乎爬虫任务"""
    try:
        logger.info("Initializing Zhihu crawler...")
        crawler = ZhihuCrawler(raw_cookie_str)
        logger.info("Fetching hot list...")
        hot_json = await crawler.zhihu_hot()
        logger.info("Fetching question list...")
        question_json = await crawler.question_detail_many(question_urls(hot_json))
        logger.info("Fetching author list...")
        author_json = await crawler.author_info_many(author_urls(question_json))
        logger.info("save info...")
        save_json(question_json, hot_json, author_json)



    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise


if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
