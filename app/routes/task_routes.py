from flask import Blueprint, request, abort, make_response
from ..db import db
from ..models.task import Task
from datetime import datetime
from .route_utilities import (
    validate_model, create_model, send_slack_message,
    get_models_with_filters, delete_model, no_content_response)        #Wave 7 refactoring

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

'''Wave 1 CRUD Routes'''

@bp.post("")
def create_task():
    #Wave 7 refactor X request_body = request.get_json()
    return create_model(Task, request.get_json())

'''Wave 2 Update get_all_tasks'''
@bp.get("")
def get_all_tasks():
    #Wave 7 refactor, moved code to get_models_with_filters
    return get_models_with_filters(Task, request.args)

@bp.get("/<task_id>")
def get_one_task(task_id):
    #Wave 7 refactor, task = validate_model(Task, task_id)
    return validate_model(Task, task_id).to_dict()

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    try:
        task.title = request_body["title"]
        task.description = request_body["description"]
        if "completed_at" in request_body:
            task.completed_at = Task.parse_completed_at(request_body["completed_at"])
    except (KeyError, ValueError, TypeError):
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.commit()

    #Wave 7 refactor, return Response(status=204, mimetype="application/json")
    return no_content_response()

@bp.delete("/<task_id>")
def delete_task(task_id):
    return delete_model(Task, task_id)


'''Wave 3 Custom Endpoints'''

@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    db.session.commit()

    '''Wave 4 slack complete'''
    send_slack_message(f"Someone just completed the task {task.title}")

    #Wave 7 refactor, return Response(status=204, mimetype="application/json")
    return no_content_response()


@bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    #Wave 7 refactor, return Response(status=204, mimetype="application/json")
    return no_content_response()
