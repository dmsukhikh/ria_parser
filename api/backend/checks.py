# this file is for request checks
import flask

# checks
def query_checks() -> bool:
    if "date" in flask.request.args.keys() and \
        ("from" in flask.request.args.keys() or \
        "to" in flask.request.args.keys()):
        return False

    if sum(x in flask.request.args.keys() for x in ["from", "to"]) == 1:
        return False

    if not flask.request.args.get("page", "0").isdecimal() or \
       not flask.request.args.get("limit", "0").isdecimal():
        return False

    return True
