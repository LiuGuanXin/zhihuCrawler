import json
import re
import logging
from typing import Dict, List, Optional, Any
from functools import wraps

from tenacity import retry, stop_after_attempt, wait_exponential

from crawl4ai import (
    AsyncWebCrawler, CacheMode, CrawlerRunConfig,
    JsonCssExtractionStrategy, MemoryAdaptiveDispatcher, BrowserConfig
)
from crawl4ai.models import RunManyReturn

from util.tools import parse_cookies
from zhihu.schema import hot_schema, question_schema, author_schema

logger = logging.getLogger(__name__)

def retry_async(max_attempts=3, wait_min=1, wait_max=5):
    """统一的异步任务重试装饰器（指数退避）"""
    def decorator(func):
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"[重试中] {func.__name__} 失败: {e}")
                raise
        return wrapper
    return decorator

class ZhihuCrawler:
    """知乎爬虫类：支持知乎热榜、问题详情、作者信息抓取"""

    def __init__(self, cookie: str, headless: bool = False):
        """
        初始化知乎爬虫

        Args:
            cookie (str): 知乎登录 cookie 字符串
            headless (bool): 是否开启无头模式
        """
        self.cookie = cookie
        self.base_url = "https://www.zhihu.com"
        self.browser_cfg = self._create_browser_config(headless)
        self.crawler = AsyncWebCrawler(config=self.browser_cfg)

    def _create_browser_config(self, headless: bool = False) -> BrowserConfig:
        """创建浏览器配置"""
        return BrowserConfig(
            verbose=False,
            browser_type="chromium",
            cookies=parse_cookies(self.cookie),
            headless=headless
        )

    @staticmethod
    def _create_run_config(schema, js_code: Optional[List[str]] = None) -> CrawlerRunConfig:
        """创建爬虫运行配置"""
        config_dict = {
            "page_timeout": 20000,
            "delay_before_return_html": 10.0,
            "cache_mode": CacheMode.BYPASS
        }
        if js_code:
            config_dict["js_code"] = js_code
        if schema:
            config_dict["extraction_strategy"] = JsonCssExtractionStrategy(schema)
        return CrawlerRunConfig(**config_dict)

    @staticmethod
    def _create_dispatcher() -> MemoryAdaptiveDispatcher:
        """创建调度器（多任务调度用）"""
        return MemoryAdaptiveDispatcher(
            memory_threshold_percent=70.0,
            check_interval=1.0,
            max_session_permit=10
        )

    @retry_async(max_attempts=3, wait_min=1, wait_max=5)
    async def _crawl_single(self, url: str, schema) -> Optional[Any]:
        """
        爬取单个 URL

        Args:
            url (str): 需要爬取的 URL
            schema: 提取策略 schema

        Returns:
            Optional[Any]: 爬取并解析的 JSON 数据，失败时返回 None
        """
        try:
            run_config = self._create_run_config(schema)
            result = await self.crawler.arun(url=url, config=run_config)
            return json.loads(result.extracted_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {url} - {e}")
        except Exception as e:
            logger.error(f"爬取失败: {url} - {e}")
        return None

    @retry_async(max_attempts=3, wait_min=1, wait_max=5)
    async def _crawl_urls(self, urls: List[str], run_config: Optional[CrawlerRunConfig]) -> RunManyReturn:
        """
        批量爬取多个 URL

        Args:
            urls (List[str]): URL 列表
            run_config (Optional[CrawlerRunConfig]): 配置

        Returns:
            RunManyReturn: 批量任务执行结果
        """
        try:
            return await self.crawler.arun_many(
                urls=urls,
                config=run_config,
                dispatcher=self._create_dispatcher()
            )
        except Exception as e:
            logger.error(f"批量爬取失败: {e}")
            return []

    async def zhihu_hot(self) -> List[Dict]:
        """获取知乎热榜"""
        results = await self._crawl_single(f"{self.base_url}/hot", hot_schema) or []
        for result in results:
            match = re.search(r"([\d\.]+)\s*万?", result.get('heat', ''))
            if match:
                result['heat'] = match.group(1)
        return results

    async def question_detail(self, content_id: str) -> List[Dict]:
        """获取单个问题详情"""
        url = f"{self.base_url}/question/{content_id}"
        data = await self._crawl_single(url, question_schema) or []
        self._convert_question_json(data)
        return data

    async def question_detail_many(self, urls: List[str]) -> Dict[str, Any]:
        """批量获取问题详情"""
        results = await self._crawl_urls(urls, self._create_run_config(question_schema))
        result_dict = {}
        for result in results:
            try:
                data = json.loads(result.extracted_content)
                self._convert_question_json(data)
                result_dict[result.url] = data
            except json.JSONDecodeError as e:
                logger.error(f"批量问题详情 JSON 解析失败: {result.url} - {e}")
        return result_dict

    async def author_info(self, url: str) -> List[Dict]:
        """获取作者信息"""
        return await self.author_info_many([url]).get(url, [])

    async def author_info_many(self, urls: List[str]) -> Dict[str, Any]:
        """批量获取作者信息"""
        js_code = [
            'document.querySelector("#ProfileHeader > div > div.ProfileHeader-wrapper > '
            'div > div.ProfileHeader-content > div.ProfileHeader-contentFooter > button")?.click();'
        ]
        run_config = self._create_run_config(author_schema, js_code)
        results = await self._crawl_urls(urls, run_config)
        result_dict = {}
        for result in results:
            try:
                data = json.loads(result.extracted_content)
                self._convert_author_info_json(data)
                result_dict[result.url] = data
            except json.JSONDecodeError as e:
                logger.error(f"作者信息 JSON 解析失败: {result.url} - {e}")
        return result_dict

    @staticmethod
    def _convert_author_info_json(raw_json: List[Dict[str, Any]]) -> None:
        """格式化知乎作者信息 JSON 数据"""
        PREFIX_TO_FIELD = {
            '居住地': 'location',
            '所在行业': 'industry',
            '职业经历': 'occupation',
            '教育经历': 'education',
            '个人简介': 'description'
        }

        for item in raw_json:
            item['user_name'] = item.get('user_name', '').replace('\u200b', '')
            gender_str = item.get('gender', '')
            item['gender'] = '男' if '他' in gender_str else '女' if '她' in gender_str else '未知'

            # 收集动态字段
            info = []
            for idx in range(1, 100):
                key = f'list{idx}'
                if key in item:
                    info.append(item.pop(key))
                else:
                    break

            for info_str in info:
                for prefix, field in PREFIX_TO_FIELD.items():
                    if info_str.startswith(prefix):
                        item[field] = info_str[len(prefix):]
                        break

    @staticmethod
    def _convert_question_json(raw_json: List[Dict[str, Any]]) -> None:
        """格式化知乎问题 JSON 数据"""
        for item in raw_json:
            try:
                item['title_info'] = json.loads(item.get('title_info', '{}'))
            except json.JSONDecodeError:
                item['title_info'] = {}

            if not item.get('author_url', '').startswith('http'):
                item['author_url'] = f"https:{item['author_url']}"

            vote_text = item.pop('vote_count', '')
            approval_match = re.search(r'赞同\s*(\d+)', vote_text)
            comment_match = re.search(r'(\d+)\s*条评论', vote_text)

            item['approval_count'] = int(approval_match.group(1)) if approval_match else 0
            item['comment_count'] = int(comment_match.group(1)) if comment_match else 0
