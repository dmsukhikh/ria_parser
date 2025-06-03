# this file is for orm definitions
import datetime
from backend.basic import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Text, DateTime, ForeignKey, UniqueConstraint

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

