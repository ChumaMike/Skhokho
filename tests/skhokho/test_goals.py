from app.models import Goal, User

def test_create_new_mission(client, auth, app):
    """QA: Can a user define a new mission?"""
    # 1. Login
    auth.register(username="dreamer", password="password123")
    auth.login(username="dreamer", password="password123")

    # 2. Create Goal (POST request)
    # We follow the redirect to see the dashboard success message
    response = client.post('/goals/add', data={
        'title': 'Learn Pytest',
        'description': 'Master automated testing for Skhokho',
    }, follow_redirects=True)

    # 3. Check UI Feedback
    assert response.status_code == 200
    assert b"Mission Initialized" in response.data or b"Active Missions" in response.data

    # 4. Check Database Memory
    # We look inside the DB to make sure it wasn't a hallucination
    with app.app_context():
        goal = Goal.query.filter_by(title="Learn Pytest").first()
        assert goal is not None
        assert goal.description == "Master automated testing for Skhokho"
        assert goal.is_completed is False

def test_dashboard_shows_goals(client, auth, app):
    """QA: Do goals actually appear on the Neural Core?"""
    auth.register(username="achiever", password="password123")
    auth.login(username="achiever", password="password123")

    # 1. Create a goal directly in DB (faster than using the form)
    with app.app_context():
        user = User.query.filter_by(username="achiever").first()
        new_goal = Goal(title="Get 5 Green Dots", user_id=user.id)
        # Note: We must add to the session used by the test 'app' context
        # But since our conftest handles sessions weirdly, let's use the client to be safe
    
    client.post('/goals/add', data={'title': 'Get 5 Green Dots'})

    # 2. Visit the Goals Dashboard
    response = client.get('/goals/', follow_redirects=True) 
    # (Note: Check if your route is /goals/ or /goals/dashboard)

    # 3. Verify it's visible
    assert b"Get 5 Green Dots" in response.data

def test_complete_mission(client, auth, app):
    """QA: Can a user check off a mission?"""
    auth.register(username="closer", password="password123")
    auth.login(username="closer", password="password123")

    # 1. Create Goal
    client.post('/goals/add', data={'title': 'Finish Hackathon'})
    
    # 2. Get the Goal ID from DB
    with app.app_context():
        goal = Goal.query.filter_by(title="Finish Hackathon").first()
        goal_id = goal.id

    # 3. Mark as Complete (Click the button)
    response = client.get(f'/goals/complete/{goal_id}', follow_redirects=True)

    # 4. Check UI Success Message
    assert b"Mission Accomplished" in response.data or b"Complete" in response.data

    # 5. Check Database Status
    with app.app_context():
        goal = Goal.query.get(goal_id)
        assert goal.is_completed is True

def test_goal_privacy(client, auth, app):
    """QA: CRITICAL - Can User A touch User B's goals?"""
    # 1. User A creates a goal
    auth.register(username="user_A", password="password123")
    auth.login(username="user_A", password="password123")
    client.post('/goals/add', data={'title': 'Secret Plan A'})
    
    with app.app_context():
        goal_a = Goal.query.filter_by(title="Secret Plan A").first()
        goal_a_id = goal_a.id
    
    auth.logout()

    # 2. User B logs in
    auth.register(username="user_B", password="password123")
    auth.login(username="user_B", password="password123")

    # 3. User B tries to complete User A's goal
    response = client.get(f'/goals/complete/{goal_a_id}', follow_redirects=True)

    # 4. Should NOT show success message
    # It should probably show an error or just do nothing (depending on your code)
    assert b"Mission Accomplished" not in response.data
    
    # 5. Verify DB: Goal A should still be incomplete
    with app.app_context():
        goal_a = Goal.query.get(goal_a_id)
        assert goal_a.is_completed is False