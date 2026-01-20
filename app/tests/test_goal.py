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

