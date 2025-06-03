# this file is for handlers
import re
import datetime
from backend.orm import * 
from sqlalchemy import Date, Select, between, func, select

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

def page_handle(query: Select, page_str: str, limit_str: str) -> Select:
    if (page_str == "" or int(page_str) <= 0):
        page = 1
    else:
        page = int(page_str)

    if (limit_str == "" or int(limit_str) <= 0):
        limit = 10
    else:
        limit = int(limit_str)

    print(page)

    return query.order_by(Article.id).slice((page-1)*limit, page*limit)
