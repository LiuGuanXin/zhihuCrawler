import json
import re
from typing import Dict, List, Optional, Any, Coroutine, AsyncGenerator

from crawl4ai import (
    AsyncWebCrawler, CacheMode, CrawlerRunConfig,
    JsonCssExtractionStrategy, MemoryAdaptiveDispatcher, BrowserConfig
)
from crawl4ai.models import RunManyReturn

from util.tools import parse_cookies
from zhihu.schema import hot_schema, question_schema, author_schema


class ZhihuCrawler:
    """知乎爬虫类，用于获取知乎热榜和问题详情"""

    def __init__(self, cookie: str, headless: bool = False):
        """
        初始化知乎爬虫

        Args:
            cookie: 知乎登录 cookie 字符串
        """
        self.cookie = cookie
        self.base_url = "https://www.zhihu.com"
        self.browser_cfg = self._create_browser_config(headless)
        self.crawler = AsyncWebCrawler(config=self.browser_cfg)

    def _create_browser_config(self, headless: bool = False) -> BrowserConfig:
        """创建浏览器配置"""
        config = {
            "verbose": False,
            "browser_type": "chromium",
            "cookies": parse_cookies(self.cookie),
            "headless": headless
        }
        return BrowserConfig(**config)

    @staticmethod
    def _create_run_config(schema, js_code: List[str] = None) -> CrawlerRunConfig:
        """创建爬虫运行配置"""
        config_dict = {
            "page_timeout" : 20000,
            "delay_before_return_html" : 10.0,
            "cache_mode" : CacheMode.BYPASS
        }
        if js_code is not None:
            config_dict["js_code"] = js_code
        if schema is not None:
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

    async def _crawl_single(self, url: str, schema) -> Any:
        """
        爬取单个 URL
        Args:
            url: 需要爬取的 URL
            schema: 提取策略 schema
        """
        run_config = self._create_run_config(schema)
        result = await self.crawler.arun(
            url=url,
            config=run_config
        )
        data = json.loads(result.extracted_content)
        return data

    async def _crawl_urls(self, urls: List[str], run_config: Optional[CrawlerRunConfig]) -> RunManyReturn:
        """
        批量爬取多个 URL
        Args:
            urls: URL 列表
            run_config: 配置
        """
        results = await self.crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=self._create_dispatcher()
        )
        return results

    async def zhihu_hot(self) -> List[Dict]:
        """获取知乎热榜"""
        results = await self._crawl_single(f"{self.base_url}/hot", hot_schema)
        for index, result in enumerate(results):
            match = re.search(r"([\d\.]+)\s*万?", result['heat'])
            value = match.group(1)
            result['heat'] = value
        return results

    async def question_detail(self, content_id: str) -> List[Dict]:
        """获取单个问题详情"""
        url = f"{self.base_url}/question/{content_id}"
        data = await self._crawl_single(url, question_schema)
        self._convert_question_json(data)
        return data

    async def question_detail_many(self, urls: List[str]) -> Dict[str, Any]:
        """批量获取问题详情"""
        results = await self._crawl_urls(urls, self._create_run_config(question_schema))
        result_dict = {}
        for result in results:
            data = json.loads(result.extracted_content)
            self._convert_question_json(data)
            result_dict[result.url] = data
        return result_dict

    async def author_info(self, url: str) -> List[Dict]:
        """获取作者信息"""
        run_config = CrawlerRunConfig(
            js_code=[
                'document.querySelector("#ProfileHeader > div > div.ProfileHeader-wrapper > '
                'div > div.ProfileHeader-content > div.ProfileHeader-contentFooter > button")?.click();'
            ],
            extraction_strategy=JsonCssExtractionStrategy(author_schema)
        )
        result = await self.crawler.arun(url=url, config=run_config)
        data = json.loads(result.extracted_content)
        self._convert_author_info_json(data)
        return data

    async def author_info_many(self, urls: List[str]) -> Dict[str, Any]:
        """获取作者信息"""
        js_code=[
            'document.querySelector("#ProfileHeader > div > div.ProfileHeader-wrapper > '
            'div > div.ProfileHeader-content > div.ProfileHeader-contentFooter > button")?.click();'
        ]
        run_config = self._create_run_config(author_schema, js_code)
        results = await self._crawl_urls(urls, run_config)
        result_dict = {}
        for result in results:
            data = json.loads(result.extracted_content)
            self._convert_author_info_json(data)
            result_dict[result.url] = data
        print(result_dict)
        return result_dict

    @staticmethod
    def _convert_author_info_json(raw_json: List[Dict[str, Any]]) -> None:
        """格式化知乎作者信息 JSON 数据"""
        # 定义前缀到字段名的映射
        PREFIX_TO_FIELD = {
            '居住地': 'location',
            '所在行业': 'industry',
            '职业经历': 'occupation',
            '教育经历': 'education',
            '个人简介': 'description'
        }

        for item in raw_json:
            # 1. 清理用户名中的零宽空格
            item['user_name'] = item['user_name'].replace('\u200b', '')

            # 2. 解析性别信息
            gender_str = item['gender']
            item['gender'] = '男' if '他' in gender_str else '女' if '她' in gender_str else '未知'

            # 3. 提取动态字段 (list1, list2, ...)
            info = []
            start = 1
            list_key = f'list{start}'
            while list_key in item:
                info.append(item.pop(list_key))
                start += 1
                list_key = f'list{start}'

            # 4. 根据前缀分类信息
            for info_str in info:
                for prefix, field in PREFIX_TO_FIELD.items():
                    if info_str.startswith(prefix):
                        item[field] = info_str[len(prefix):]
                        break

    @staticmethod
    def _convert_question_json(raw_json: List[Dict[str, Any]]) -> None:
        """格式化知乎问题 JSON 数据"""
        for item in raw_json:
            # 解析 title_info
            item['title_info'] = json.loads(item['title_info'])

            # 修正作者链接
            if not item['author_url'].startswith('http'):
                item['author_url'] = f"https:{item['author_url']}"

            # 解析点赞和评论数
            vote_text = item.pop('vote_count', '')
            approval_match = re.search(r'赞同\s*(\d+)', vote_text)
            comment_match = re.search(r'(\d+)\s*条评论', vote_text)

            item['approval_count'] = int(approval_match.group(1)) if approval_match else 0
            item['comment_count'] = int(comment_match.group(1)) if comment_match else 0
