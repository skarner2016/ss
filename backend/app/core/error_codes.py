class ErrorCode:
    # 参数错误 1xxx
    PARAM_ERROR = (1001, "参数错误")
    EMAIL_FORMAT_ERROR = (1002, "邮箱格式不正确")
    PASSWORD_TOO_SHORT = (1003, "密码长度不能少于6位")

    # 认证错误 2xxx
    UNAUTHORIZED = (2001, "未登录")
    PASSWORD_ERROR = (2002, "密码错误")
    USER_DISABLED = (2003, "账号已禁用")
    USER_CANCELLED = (2004, "账号已注销")

    # 资源错误 3xxx
    POST_NOT_FOUND = (3001, "帖子不存在")
    COMMENT_NOT_FOUND = (3002, "评论不存在")
    REPLY_NOT_FOUND = (3003, "回复不存在")
    NO_PERMISSION = (3004, "无权限操作")

    # 重复操作 4xxx
    ALREADY_LIKED = (4001, "已经点过赞了")
    NOT_LIKED = (4002, "未点赞")
    ALREADY_FAVORITED = (4003, "已经收藏过了")
    NOT_FAVORITED = (4004, "未收藏")

    # 频道错误 6xxx
    CHANNEL_NOT_FOUND = (6001, "频道不存在")
    CHANNEL_NAME_EXISTS = (6002, "频道名称已存在")
    CHANNEL_HAS_POSTS = (6003, "频道下存在帖子，无法删除")
    POST_CHANNEL_LIMIT = (6004, "每篇帖子最多关联3个频道")
    POST_CHANNEL_INVALID = (6005, "包含无效的频道ID")

    # 系统错误 5xxx
    SYSTEM_ERROR = (5000, "系统异常")
