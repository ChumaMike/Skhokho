def test_balaa_calculator_logic(client, auth, app):
    """QA: Does the Taxi Math work correctly?"""
    auth.register()
    auth.login()

    response = client.post('/tools/balaa', data={
        'fare': '20',
        'group_size': '3',
        'amounts': '20,20,50' 
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"30.00" in response.data