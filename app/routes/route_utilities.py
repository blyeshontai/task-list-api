from flask import abort, make_response, Response
from ..db import db
import os
import requests

'''Wave 1 Route Helper Methods'''

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
        abort(make_response({"message": f"{cls.__name__} {model_id} invalid"}, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        abort(make_response({"message": f"{cls.__name__} {model_id} not found"}, 404))
    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except (KeyError, ValueError, TypeError):
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201


'''Wave 4 Helper Slack'''

def send_slack_message(text):
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"},
        json={"channel": "task-notifications", "text":text}
    )


'''Wave 7 Refactoring'''
#moved code from task_routes, replased task with cls
def get_models_with_filters(cls, args):
    query = db.select(cls)

    title = args.get("title")
    if title:
        query = query.where(cls.title.ilike(f"%{title}%"))

    sort = args.get("sort")
    sort_by = args.get("sort_by")

    if sort is None and sort_by is None:
        query = query.order_by(cls.id)
    else:
        sort = sort or "asc"
        sort_by = sort_by or "title"
        if sort not in ("asc", "desc") or sort_by not in ("id", "title"):
            abort(make_response({"details": "Invalid sort parameter"}, 400))

        column = getattr(cls, sort_by)
        query = query.order_by(column.asc() if sort == "asc" else column.desc())

    models = db.session.scalars(query)
    return [model.to_dict() for model in models]


def delete_model(cls, model_id):
    model = validate_model(cls, model_id)
    db.session.delete(model)
    db.session.commit()
    return no_content_response()

def no_content_response():
    return Response(status=204, mimetype="application/json")
