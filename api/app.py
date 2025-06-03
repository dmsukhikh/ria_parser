import backend.basic
import backend.checks
import backend.handlers as handle
from backend.orm import *
import flask
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select


# application
@backend.basic.app.route("/article/<id>")
def fetch_article(id):
    with backend.basic.db.session() as s:
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

@backend.basic.app.route("/articles")
def fetch_many_articles():
    # basic checks for valid query params
    if not backend.checks.query_checks():
        return flask.jsonify({"response": "incorrect query params"})

    query = select(Article.id, Article.header, Article.url,
                   Article.publishing_date)

    # after checks, if to in list when "from" in list anyway
    if "to" in flask.request.args.keys(): 
        query = handle.from_to_handle(query, flask.request.args.get("from", ""),
                                      flask.request.args.get("to", ""))
    else:
        query = handle.date_handle(query, flask.request.args.get("date", ""))

    query = handle.tags_handle(query, flask.request.args.get("tag", ""))
    query = handle.page_handle(query, flask.request.args.get("page", ""),
                        flask.request.args.get("limit", ""))

    
    with db.session() as s:
        response = s.execute(query).all()
        to_output = flask.jsonify([item._asdict() for item in response])
        return to_output

app = backend.basic.app
