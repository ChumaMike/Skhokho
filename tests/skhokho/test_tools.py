from app.models import BalaaHistory, DiaryEntry

def test_balaa_calculator_logic(client, auth, app):
    """QA: Does the Taxi Math work correctly?"""
    auth.register()
    auth.login()

    response = client.post('/tools/balaa', data={
        'fare': '20',
        'group_size': '3',      # ✅ MATCHES HTML
        'amounts': '20,20,50'   # ✅ MATCHES HTML (was amounts_collected)
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check for the calculated change (R90 collected - R60 needed = R30 change)
    assert b"30.00" in response.data
    
def test_diary_persistence(client, auth, app):
    """QA: Can I write thoughts to the Diary?"""
    auth.register()
    auth.login()

    # 1. Write an entry
    client.post('/tools/diary', data={
        'entry_type': 'Goal',      # ✅ Changed from 'title'
        'content': 'Tests are fixed.'
    }, follow_redirects=True)

    # 2. Verify it appears
    response = client.get('/tools/diary')
    assert b"Tests are fixed" in response.data