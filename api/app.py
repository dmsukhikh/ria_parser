import datetime
import flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import URL, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import mapped_column, Mapped, relationship

app = flask.Flask(__name__)

# configuration for entering the database
app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
    database='ria',
    host='localhost',
    username='server',
    password='server52BOB',
    drivername='postgresql',
    port=8085
).render_as_string(hide_password=False)

print(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

# ORM definitions
class Article(db.Model):    
    __tablename__ = "articles"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    header : Mapped[str] = mapped_column(Text, nullable=False)
    url : Mapped[str] = mapped_column(unique=True, nullable=False)
    publishing_date : Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    content : Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationship to tags (many-to-many)
    tags = relationship("Tag", secondary="tags_of_articles", back_populates="articles")
    
    def __repr__(self):
        return f"<Article(id={self.id}, header='{self.header}...')>"

class Tag(db.Model):
    __tablename__ = "tags"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # Relationship to articles (many-to-many)
    articles = relationship("Article", secondary="tags_of_articles", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

class TagOfArticle(db.Model):
    __tablename__ = "tags_of_articles"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id : Mapped[int] = mapped_column(ForeignKey('articles.id', ondelete="CASCADE"))
    tag_id : Mapped[int] = mapped_column(ForeignKey('tags.id', ondelete="CASCADE"))

    __table_args__ = (
        UniqueConstraint('article_id', 'tag_id', name='unique_article_tag'),
    )
    
    def __repr__(self):
        return f"<TagOfArticle(article_id={self.article_id}, tag_id={self.tag_id})>"


# application

@app.route("/article/<id>")
def print_hello(id):
    with db.session() as s:
        try:
            article = s.get_one(Article, id)
            tags = [tag.name for tag in article.tags]
            return flask.jsonify({"id": article.id, "header": article.header,
                                  "url": article.url, 
                                  "publishing_date": article.publishing_date,
                                  "content": article.content, "tags": tags})
        except NoResultFound:
            s.rollback()
    return flask.jsonify({"response": "not found"})

if __name__ == '__main__':
    app.run(debug=True)
