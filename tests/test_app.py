import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Should include at least one known activity
    assert "Tennis Club" in data
    assert "Basketball Team" in data


def test_signup_for_activity_success():
    activity_name = "Tennis Club"
    email = "newstudent@mergington.edu"

    # Ensure clean state for this email
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_already_signed_up():
    activity_name = "Tennis Club"
    email = "duplicate@mergington.edu"

    # Ensure the email is already present
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity():
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "someone@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_participant_success():
    activity_name = "Tennis Club"
    email = "remove-me@mergington.edu"

    # Ensure the email is present to be removed
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_not_found():
    activity_name = "Tennis Club"
    email = "not-registered@mergington.edu"

    # Ensure the email is not present
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found for this activity"
