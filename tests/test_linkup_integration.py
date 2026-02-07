def test_linkup_module_loaded(client, auth_client):
    """
    Goal: Check if LinkUp is reachable and the module is loaded.
    """
    # 1. Test if the map page loads (Requires Login)
    response = auth_client.get('/linkup/') 
    
    # We expect a 200 OK status
    assert response.status_code == 200
    
    # We expect to see "LinkUp" text in the HTML
    assert b"LinkUp" in response.data

def test_linkup_provider_dashboard_redirect(auth_client):
    """
    Goal: Check if a new user is redirected to 'Join' page
    when trying to access the provider dashboard.
    """
    # Try to access dashboard without being a provider
    response = auth_client.get('/linkup/dashboard', follow_redirects=True)
    
    # Should land on the "Join" page or "Map" page depending on logic
    # Let's check if we see the form text
    assert response.status_code == 200
    # Assuming the join page has "Business Name" input
    assert b"Business Name" in response.data or b"Join" in response.data