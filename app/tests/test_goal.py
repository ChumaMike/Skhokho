from app.models import Goal, User

def test_create_goal(client, auth, app):
    """Test creating a new strategic goal."""
    auth.register()
    auth.login()

    response = client.post('/goals/', data={
        'title': 'Master Python',
        'category': 'Career',
        'target_date': '2025-12-31'
    }, follow_redirects=True)

    assert b"New objective initialized" in response.data
    
    with app.app_context():
        goal = Goal.query.first()
        assert goal.title == "Master Python"
        assert goal.progress == 0



def test_delete_goal_security(client, auth, app):
    """Test that User A cannot delete User B's goal."""
    # 1. Register User A and create a goal
    auth.register(username='userA', password='password')
    auth.login(username='userA', password='password')
    client.post('/goals/', data={'title': 'User A Goal', 'category': 'Career'})
    
    with app.app_context():
        goal_id = Goal.query.first().id
    
    auth.logout()

    # 2. Register User B and try to delete User A's goal
    auth.register(username='userB', password='password')
    auth.login(username='userB', password='password')
    
    # Try to delete the goal (Assuming URL pattern is /goals/<id>/delete)
    response = client.get(f'/goals/{goal_id}/delete', follow_redirects=True)

    # 3. Verify the goal still exists
    with app.app_context():
        assert Goal.query.get(goal_id) is not None