import pytest
from app.extensions import db
from app.models import Goal

def test_add_goal(client, auth):
    """QA: Can we create a new mission?"""
    auth.register()
    auth.login()

    # ✅ FIX: Post to '/goals/add', not '/goals/dashboard'
    response = client.post('/goals/add', data={
        'title': 'Learn Python',
        'description': 'Master Flask'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Mission Added" in response.data
    assert b"Learn Python" in response.data

def test_complete_mission(client, auth, app):
    """QA: Can we mark a mission as complete?"""
    auth.register()
    auth.login()

    # 1. Add (Using the correct route)
    client.post('/goals/add', data={'title': 'Run 5km'})
    
    # 2. Get ID
    with app.app_context():
        goal = Goal.query.filter_by(title='Run 5km').first()
        # Safety check: If goal is None, the add failed (likely due to route mismatch previously)
        assert goal is not None
        goal_id = goal.id

    # 3. Complete
    response = client.get(f'/goals/complete/{goal_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Mission Accomplished" in response.data

    # 4. Verify DB
    with app.app_context():
        goal = db.session.get(Goal, goal_id)
        assert goal.is_completed is True