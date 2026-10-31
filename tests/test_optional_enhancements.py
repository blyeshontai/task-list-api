from app.models.task import Task
from app.db import db
import pytest

#!!! I did not write the tests, tests were made with AI!!!#
# ----- completed_at edge cases -----

def test_create_task_with_valid_completed_at(client):
    response = client.post("/tasks", json={
        "title": "Done already",
        "description": "Finished it",
        "completed_at": "2026-10-31T12:00:00"
    })
    response_body = response.get_json()

    assert response.status_code == 201
    assert response_body["is_complete"] == True


def test_create_task_with_invalid_completed_at(client):
    response = client.post("/tasks", json={
        "title": "Bad date",
        "description": "Should fail",
        "completed_at": "not a date"
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {"details": "Invalid data"}
    assert db.session.scalars(db.select(Task)).all() == []


def test_update_task_with_valid_completed_at(client, one_task):
    response = client.put("/tasks/1", json={
        "title": "Updated",
        "description": "Updated",
        "completed_at": "2026-10-31T12:00:00"
    })
    assert response.status_code == 204

    response_body = client.get("/tasks/1").get_json()
    assert response_body["is_complete"] == True


def test_update_task_with_invalid_completed_at(client, one_task):
    response = client.put("/tasks/1", json={
        "title": "Updated",
        "description": "Updated",
        "completed_at": "not a date"
    })
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {"details": "Invalid data"}

    task = client.get("/tasks/1").get_json()
    assert task["title"] == "Go on my daily walk 🏞"      # unchanged


# ----- query params -----

def test_get_tasks_invalid_sort(client, three_tasks):
    response = client.get("/tasks?sort=banana")
    response_body = response.get_json()

    assert response.status_code == 400
    assert response_body == {"details": "Invalid sort parameter"}


def test_get_tasks_sorted_by_id_desc(client, three_tasks):
    response = client.get("/tasks?sort_by=id&sort=desc")
    response_body = response.get_json()

    assert response.status_code == 200
    assert [task["id"] for task in response_body] == [3, 2, 1]


def test_get_tasks_filtered_by_title(client, three_tasks):
    response = client.get("/tasks?title=GARDEN")           # different case on purpose
    response_body = response.get_json()

    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body[0]["title"] == "Water the garden 🌷"


def test_get_goals_sorted_by_title(client):
    for title in ["Read more", "Exercise", "Learn Flask"]:
        client.post("/goals", json={"title": title})

    response = client.get("/goals?sort=asc")
    response_body = response.get_json()

    assert response.status_code == 200
    assert [goal["title"] for goal in response_body] == ["Exercise", "Learn Flask", "Read more"]
