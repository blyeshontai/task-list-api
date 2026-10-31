from flask import Blueprint, request
from ..db import db
from ..models.goal import Goal
from ..models.task import Task
from .route_utilities import (
    validate_model, create_model,
    get_models_with_filters, delete_model, no_content_response)        #Wave 7 refactor

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

'''Wave 5 CRUD Routes'''

@bp.post("")
def create_goal():
    return create_model(Goal, request.get_json())

@bp.get("")
def get_all_goals():
    return get_models_with_filters(Goal, request.args)


@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    return validate_model(Goal, goal_id).to_dict()

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    goal.title = request.get_json()["title"]
    db.session.commit()

    return no_content_response()

@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    return delete_model(Goal, goal_id)


'''Wave 6 Routes'''
@bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    task_ids = request.get_json()["task_ids"]

    goal.tasks = [validate_model(Task, task_id) for task_id in task_ids]
    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }, 200

@bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    response = goal.to_dict()
    response["tasks"] = [task.to_dict() for task in goal.tasks]
    return response
