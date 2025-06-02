CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    header TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    publishing_date TIMESTAMP NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tags_of_articles (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_articles_publishing_date_date
ON articles ((publishing_date::date));

-- Для того, чтобы мы случайно не добавили дубликат в tags_of_articles
CREATE UNIQUE INDEX IF NOT EXISTS unique_article_tag 
ON tags_of_articles(article_id, tag_id);

-- Создадим пользователя
CREATE USER server;
GRANT ALL ON ALL TABLES IN SCHEMA public TO crawler;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO crawler;

