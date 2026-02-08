def test_map_interface_loads(client, auth):
    """QA: Does the LinkUp dashboard render?"""
    auth.register()
    auth.login()
    
    response = client.get('/linkup/', follow_redirects=True)
    assert response.status_code == 200
    # We look for the unique CSS ID for the map container
    assert b'id="map"' in response.data or b'LinkUp' in response.data