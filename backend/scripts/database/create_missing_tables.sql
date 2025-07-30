-- PeerPortal 留学平台缺失数据库表创建脚本
-- 执行前请确保数据库连接正常

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER, -- 可选，用于分组对话
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system')),
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'read')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- 索引优化
    CONSTRAINT messages_sender_recipient_check CHECK (sender_id != recipient_id)
);

-- 论坛帖子表
CREATE TABLE IF NOT EXISTS forum_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    tags TEXT[] DEFAULT '{}', -- PostgreSQL 数组类型
    replies_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_hot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 论坛回复表
CREATE TABLE IF NOT EXISTS forum_replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES forum_replies(id) ON DELETE CASCADE, -- 支持嵌套回复
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 论坛点赞记录表
CREATE TABLE IF NOT EXISTS forum_likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES forum_posts(id) ON DELETE CASCADE,
    reply_id INTEGER REFERENCES forum_replies(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 确保每个用户对每个帖子/回复只能点赞一次
    CONSTRAINT forum_likes_unique_post CHECK (
        (post_id IS NOT NULL AND reply_id IS NULL) OR 
        (post_id IS NULL AND reply_id IS NOT NULL)
    ),
    CONSTRAINT forum_likes_unique_user_post UNIQUE (user_id, post_id),
    CONSTRAINT forum_likes_unique_user_reply UNIQUE (user_id, reply_id)
);

-- 文件上传记录表
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('avatar', 'document', 'other')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以优化查询性能
-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read) WHERE is_read = FALSE;

-- 论坛帖子表索引
CREATE INDEX IF NOT EXISTS idx_forum_posts_author_id ON forum_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_posts_category ON forum_posts(category);
CREATE INDEX IF NOT EXISTS idx_forum_posts_created_at ON forum_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_last_activity ON forum_posts(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_is_pinned ON forum_posts(is_pinned) WHERE is_pinned = TRUE;
CREATE INDEX IF NOT EXISTS idx_forum_posts_is_hot ON forum_posts(is_hot) WHERE is_hot = TRUE;
CREATE INDEX IF NOT EXISTS idx_forum_posts_tags ON forum_posts USING GIN(tags); -- GIN索引用于数组搜索

-- 论坛回复表索引
CREATE INDEX IF NOT EXISTS idx_forum_replies_post_id ON forum_replies(post_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_author_id ON forum_replies(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_parent_id ON forum_replies(parent_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_created_at ON forum_replies(created_at ASC);

-- 论坛点赞表索引
CREATE INDEX IF NOT EXISTS idx_forum_likes_user_id ON forum_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_likes_post_id ON forum_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_forum_likes_reply_id ON forum_likes(reply_id);

-- 文件上传表索引
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_file_type ON uploaded_files(file_type);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_created_at ON uploaded_files(created_at DESC);

-- 创建触发器以自动更新论坛帖子的统计数据
-- 更新帖子回复数量的触发器
CREATE OR REPLACE FUNCTION update_post_replies_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE forum_posts 
        SET replies_count = replies_count + 1,
            last_activity = NOW()
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE forum_posts 
        SET replies_count = replies_count - 1,
            last_activity = NOW()
        WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_post_replies_count ON forum_replies;
CREATE TRIGGER trigger_update_post_replies_count
    AFTER INSERT OR DELETE ON forum_replies
    FOR EACH ROW
    EXECUTE FUNCTION update_post_replies_count();

-- 更新点赞数量的触发器
CREATE OR REPLACE FUNCTION update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.post_id IS NOT NULL THEN
            UPDATE forum_posts 
            SET likes_count = likes_count + 1 
            WHERE id = NEW.post_id;
        ELSIF NEW.reply_id IS NOT NULL THEN
            UPDATE forum_replies 
            SET likes_count = likes_count + 1 
            WHERE id = NEW.reply_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.post_id IS NOT NULL THEN
            UPDATE forum_posts 
            SET likes_count = likes_count - 1 
            WHERE id = OLD.post_id;
        ELSIF OLD.reply_id IS NOT NULL THEN
            UPDATE forum_replies 
            SET likes_count = likes_count - 1 
            WHERE id = OLD.reply_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建点赞触发器
DROP TRIGGER IF EXISTS trigger_update_likes_count ON forum_likes;
CREATE TRIGGER trigger_update_likes_count
    AFTER INSERT OR DELETE ON forum_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_likes_count();

-- 创建视图以简化复杂查询
-- 论坛帖子列表视图 (包含作者信息)
CREATE OR REPLACE VIEW forum_posts_with_author AS
SELECT 
    fp.*,
    u.username as author_username,
    u.avatar_url as author_avatar,
    u.role as author_role
FROM forum_posts fp
JOIN users u ON fp.author_id = u.id;

-- 论坛回复列表视图 (包含作者信息)
CREATE OR REPLACE VIEW forum_replies_with_author AS
SELECT 
    fr.*,
    u.username as author_username,
    u.avatar_url as author_avatar,
    u.role as author_role
FROM forum_replies fr
JOIN users u ON fr.author_id = u.id;

-- 消息对话视图 (用于获取对话列表)
CREATE OR REPLACE VIEW message_conversations AS
SELECT DISTINCT
    CASE 
        WHEN m.sender_id < m.recipient_id 
        THEN CONCAT(m.sender_id, '_', m.recipient_id)
        ELSE CONCAT(m.recipient_id, '_', m.sender_id)
    END as conversation_key,
    LEAST(m.sender_id, m.recipient_id) as user1_id,
    GREATEST(m.sender_id, m.recipient_id) as user2_id,
    MAX(m.created_at) as last_message_time
FROM messages m
GROUP BY conversation_key, user1_id, user2_id;

-- 插入一些基础数据
-- 论坛分类数据 (如果需要单独的分类表的话)
-- CREATE TABLE IF NOT EXISTS forum_categories (
--     id VARCHAR(50) PRIMARY KEY,
--     name VARCHAR(100) NOT NULL,
--     description TEXT,
--     icon VARCHAR(10),
--     post_count INTEGER DEFAULT 0,
--     sort_order INTEGER DEFAULT 0,
--     is_active BOOLEAN DEFAULT TRUE,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- 提醒信息
DO $$
BEGIN
    RAISE NOTICE '数据库表创建完成！';
    RAISE NOTICE '已创建的表: messages, forum_posts, forum_replies, forum_likes, uploaded_files';
    RAISE NOTICE '已创建的索引: 所有主要查询优化索引';
    RAISE NOTICE '已创建的触发器: 自动更新统计数据';
    RAISE NOTICE '已创建的视图: forum_posts_with_author, forum_replies_with_author, message_conversations';
    RAISE NOTICE '请确保在应用启动前运行此脚本';
END $$;