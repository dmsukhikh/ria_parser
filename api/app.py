import datetime
import flask
import re
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import URL, Date, Select, Text, DateTime, ForeignKey, \
                       UniqueConstraint, between, func, select
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
    tags = relationship("Tag", secondary="tags_of_articles",
                        back_populates="articles", lazy="selectin")

    def __repr__(self):
        return f"<Article(id={self.id}, header='{self.header}...')>"

class Tag(db.Model):
    __tablename__ = "tags"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # Relationship to articles (many-to-many)
    articles = relationship("Article", secondary="tags_of_articles", back_populates="tags",
                            lazy="selectin")
    
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

# checks
def query_checks() -> bool:
    if "date" in flask.request.args.keys() and \
        ("from" in flask.request.args.keys() or \
        "to" in flask.request.args.keys()):
        return False

    if sum(x in flask.request.args.keys() for x in ["from", "to"]) == 1:
        return False
    return True

# handlers

def date_handle(query : Select, q : str) -> Select:
    if len(q) > 0 and not re.match(r"\d{4}-\d{2}-\d{2}", q):
        return query 

    if len(q) == 0:
        t = datetime.date.today()
        q_prep = [t.year, t.month, t.day]
    else:
        q_prep = [int(i) for i in q.split('-')]

    q_date = datetime.date(year=q_prep[0], month=q_prep[1], day=q_prep[2])
    return query.where(
        func.cast(Article.publishing_date, Date) == q_date)

def from_to_handle(query : Select, fr : str, to : str) -> Select:
    if not all(re.match(r"\d{4}-\d{2}-\d{2}", q) for q in [fr, to]):
        return query 
    from_prep = [int(i) for i in fr.split('-')]
    to_prep = [int(i) for i in to.split('-')]

    from_date = datetime.date(year=from_prep[0], month=from_prep[1], day=from_prep[2])
    to_date = datetime.date(year=to_prep[0], month=to_prep[1], day=to_prep[2])

    return query.where(
        between(func.cast(Article.publishing_date, Date), from_date, to_date))

def tags_handle(query: Select, tag: str) -> Select:
    if tag == "":
        return query
    tags = tag.split(',')
    
    subquery = select(TagOfArticle.article_id).join(
        Tag, (TagOfArticle.tag_id == Tag.id) & (Tag.name.in_(tags)))

    return query.where(Article.id.in_(subquery))


# application

@app.route("/article/<id>")
def fetch_article(id):
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

@app.route("/articles")
def fetch_many_articles():
    # basic checks for valid query params
    if not query_checks():
        return flask.jsonify({"response": "incorrect query params"})

    query = select(Article.id, Article.header, Article.url,
                   Article.publishing_date)

    # after checks, if to in list when "from" in list anyway
    if "to" in flask.request.args.keys(): 
        query = from_to_handle(query, flask.request.args.get("from", ""),
                                      flask.request.args.get("to", ""))
    else:
        query = date_handle(query, flask.request.args.get("date", ""))

    query = tags_handle(query, flask.request.args.get("tag", ""))

    
    with db.session() as s:
        response = s.execute(query).all()
        to_output = flask.jsonify([item._asdict() for item in response])
        return to_output

if __name__ == '__main__':
    app.run(debug=True)
