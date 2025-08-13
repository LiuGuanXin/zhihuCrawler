# 知乎爬虫项目 (ZhihuCrawler)

这是一个用于爬取知乎热榜、问题详情和用户信息的Python爬虫工具。

## 功能特性

- 获取知乎热榜数据
- 批量爬取问题详情
- 批量爬取用户信息
- 数据自动保存为JSON格式
- 支持异步并发爬取
- 自动重试机制

## 项目结构

```
.
├── main.py                # 主程序入口
├── zhihu/
│   ├── ZhihuCrawler.py    # 知乎爬虫核心实现
│   └── schema.py          # 数据解析schema
├── util/
│   └── tools.py           # 工具函数
└── output/                # 数据输出目录
    └── YYYY-MM-DD_HHMMSS/ # 按时间戳生成的输出目录
        ├── hot_list.json      # 热榜数据
        ├── question_details.json # 问题详情
        └── author_json.json   # 用户信息
```

## 使用说明

### 前提条件

1. 安装Python 3.7+
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

### 获取知乎Cookie

1. 登录知乎网站
2. 从浏览器开发者工具中复制cookie字符串
3. 粘贴到`main.py`中的`raw_cookie_str`变量

### 运行爬虫

```bash
python main.py
```

程序会自动执行以下步骤:
1. 爬取知乎热榜
2. 获取热榜中所有问题的详情
3. 获取这些问题相关用户的信息
4. 将数据保存到`output`目录下的时间戳子目录中

## 数据格式说明

### 热榜数据 (hot_list.json)

```json
{
  "title": "问题标题",
  "url": "问题URL",
  "heat": "热度值",
  "excerpt": "问题摘要"
}
```

### 问题详情 (question_details.json)

```json
{
  "title": "问题标题",
  "content": "问题内容",
  "author_name": "提问者名称",
  "author_url": "提问者主页URL",
  "approval_count": 赞同数,
  "comment_count": 评论数
}
```

### 用户信息 (author_json.json)

```json
{
  "user_name": "用户名",
  "gender": "性别",
  "location": "居住地",
  "industry": "所在行业",
  "occupation": "职业经历",
  "education": "教育经历",
  "description": "个人简介"
}
```

## 高级配置

1. 修改`main.py`中的日志级别
2. 调整`ZhihuCrawler.py`中的爬虫参数:
   - 重试次数(`max_attempts`)
   - 请求间隔(`wait_min`, `wait_max`)
   - 并发控制(`max_session_permit`)

## 注意事项

1. 请合理使用爬虫，避免对知乎服务器造成过大压力
2. 知乎可能会更新页面结构，需要相应更新schema
3. 长期使用时建议定期更新cookie