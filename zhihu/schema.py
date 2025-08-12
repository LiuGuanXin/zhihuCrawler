hot_schema = {
    "name": "Zhihu Hot Item",
    "baseSelector": "div.HotItem-content",  # 主容器
    "fields": [
        { "name": "title", "selector": "h2.HotItem-title", "type": "text" },
        { "name": "url", "selector": "a", "type": "attribute", "attribute": "href" },
        { "name": "excerpt", "selector": "p.HotItem-excerpt", "type": "text" },
        { "name": "heat", "selector": "div.HotItem-metrics", "type": "text" },
    ]
}



question_schema = {
    "name": "Zhihu Question Page",
    "baseSelector": "div.List-item",
    "fields": [
        {
            "name": "title_info",
            "selector": "div.ContentItem.AnswerItem",
            "type": "attribute",
            "attribute": "data-zop"
        },
        {
            "name": "author_url",
            "selector": "a.UserLink-link",
            "type": "attribute",
            "attribute": "href"
        },
        {
            "name": "author_avatar",
            "selector": "img.Avatar.AuthorInfo-avatar.css-1hx3fyn",
            "type": "attribute",
            "attribute": "srcset"
        },
        {
            "name": "content",
            "selector": "div.css-376mun",
            "type": "text"
        },
        {
            "name": "vote_count",
            "selector": "div.ContentItem-actions",
            "type": "text"
        }
    ]
}

author_schema = {
    "name": "Zhihu Author Page",
    "baseSelector": "#ProfileHeader > div",
    "fields": [
        {
            "name": "user_name",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentHead > h1 > span.ProfileHeader-name",
            "type": "text"
        },
        {
            "name": "ip",
            "selector": "div.ProfileHeader-userCover > div > div > span",
            "type": "text"
        },
        {
            "name": "signature",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentHead > h1 > span.ztext.ProfileHeader-headline",
            "type": "text"
        },
        {
            "name": "gender",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentFooter > div > button.Button.FollowButton.FEfUrdfMIKpQDJDqkjte.Button--primary.Button--blue.epMJl0lFQuYbC7jrwr_o.JmYzaky7MEPMFcJDLNMG",
            "type": "text"
        },
        {
            "name": "list1",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(1)",
            "type": "text"
        },
        {
            "name": "list2",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(2)",
            "type": "text"
        },
        {
            "name": "list3",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(3)",
            "type": "text"
        },
        {
            "name": "list4",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(4)",
            "type": "text"
        },
        {
            "name": "list5",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(5)",
            "type": "text"
        },
        {
            "name": "list6",
            "selector": "div.ProfileHeader-wrapper > div > div.ProfileHeader-content > div.ProfileHeader-contentBody > div > div > div:nth-child(6)",
            "type": "text"
        }
    ]
}