-- 社区系统数据库建表语句

-- 用户表
CREATE TABLE users (
    id            BIGSERIAL PRIMARY KEY,              -- 用户ID
    email         VARCHAR(255) UNIQUE NOT NULL,       -- 邮箱，用于登录
    password_hash VARCHAR(255) NOT NULL,              -- 密码哈希，bcrypt加密
    nickname      VARCHAR(50),                        -- 用户昵称，可选
    avatar_url    VARCHAR(500),                       -- 用户头像URL
    bio           VARCHAR(500),                       -- 个人简介
    status        SMALLINT DEFAULT 1,                 -- 状态：0=禁用，1=正常，2=已注销
    created_at    TIMESTAMPTZ DEFAULT NOW(),          -- 创建时间
    updated_at    TIMESTAMPTZ DEFAULT NOW()           -- 最后更新时间
);

-- 帖子表
CREATE TABLE posts (
    id            BIGSERIAL PRIMARY KEY,              -- 帖子ID
    user_id       BIGINT,                             -- 作者用户ID
    title         VARCHAR(200) NOT NULL,              -- 帖子标题
    content       TEXT NOT NULL,                      -- 帖子内容
    like_count    INT DEFAULT 0,                      -- 点赞数量，冗余字段，写时更新
    comment_count INT DEFAULT 0,                      -- 评论数量，冗余字段，写时更新
    status        SMALLINT DEFAULT 0,                 -- 审核状态：0=待审核，1=已通过，2=已拒绝
    deleted_at    TIMESTAMPTZ,                        -- 软删除时间，NULL表示未删除
    created_at    TIMESTAMPTZ DEFAULT NOW(),          -- 创建时间
    updated_at    TIMESTAMPTZ DEFAULT NOW()           -- 最后更新时间
);

-- 评论表（一级评论）
CREATE TABLE comments (
    id            BIGSERIAL PRIMARY KEY,              -- 评论ID
    post_id       BIGINT,                             -- 所属帖子ID
    user_id       BIGINT,                             -- 评论者用户ID
    content_type  SMALLINT DEFAULT 1,                 -- 评论内容类型：1=纯文本，2=图片/视频
    content       TEXT NOT NULL,                      -- 评论内容
    reply_count   INT DEFAULT 0,                      -- 回复数量，冗余字段，写时更新
    status        SMALLINT DEFAULT 0,                 -- 审核状态：0=待审核，1=已通过，2=已拒绝
    deleted_at    TIMESTAMPTZ,                        -- 软删除时间，NULL表示未删除
    created_at    TIMESTAMPTZ DEFAULT NOW()           -- 创建时间
);

-- 回复表（二级回复）
CREATE TABLE replies (
    id              BIGSERIAL PRIMARY KEY,            -- 回复ID
    comment_id      BIGINT,                           -- 所属一级评论ID
    user_id         BIGINT,                           -- 回复者用户ID
    reply_to_user_id BIGINT,                          -- 被回复用户ID，用于展示@某人
    content_type    SMALLINT DEFAULT 1,               -- 评论内容类型：1=纯文本，2=图片/视频
    content         TEXT NOT NULL,                    -- 回复内容
    status          SMALLINT DEFAULT 0,               -- 审核状态：0=待审核，1=已通过，2=已拒绝
    deleted_at      TIMESTAMPTZ,                      -- 软删除时间，NULL表示未删除
    created_at      TIMESTAMPTZ DEFAULT NOW()         -- 创建时间
);

-- 点赞表（多态）
CREATE TABLE likes (
    id            BIGSERIAL PRIMARY KEY,              -- 点赞记录ID
    user_id       BIGINT,                             -- 点赞用户ID
    target_type   SMALLINT NOT NULL,                  -- 目标类型：1=帖子，2=评论，3=回复
    target_id     BIGINT NOT NULL,                    -- 目标ID
    created_at    TIMESTAMPTZ DEFAULT NOW(),          -- 点赞时间
    UNIQUE(user_id, target_type, target_id)
);

-- 收藏表
CREATE TABLE favorites (
    id            BIGSERIAL PRIMARY KEY,              -- 收藏记录ID
    user_id       BIGINT,                             -- 收藏用户ID
    post_id       BIGINT,                             -- 收藏帖子ID
    created_at    TIMESTAMPTZ DEFAULT NOW(),          -- 收藏时间
    UNIQUE(user_id, post_id)
);
