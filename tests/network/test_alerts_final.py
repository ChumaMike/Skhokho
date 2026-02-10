from app.models import NetworkContact, NetworkAlert
from datetime import datetime, timedelta

def test_add_alert_working(client, auth, app):
    """Test that uses the working auth fixture"""
    auth.register()
    auth.login()
    
    # Add contact
    client.post('/linkup/network/add_contact', data={
        'name': 'Test Contact',
        'role': 'Test Role',
        'phone': '1234567890',
        'email': 'test@example.com'
    })
    
    # Verify contact exists
    with app.app_context():
        contact = NetworkContact.query.filter_by(name='Test Contact').first()
        assert contact is not None
    
    # Add alert
    alert_date = datetime.now() + timedelta(days=1)
    alert_date_str = alert_date.strftime('%Y-%m-%dT%H:%M')
    
    response = client.post(f'/linkup/network/add_alert/{contact.id}', data={
        'alert_title': 'Test Alert',
        'alert_description': 'Test Description',
        'alert_type': 'Call',
        'alert_date': alert_date_str
    }, follow_redirects=True)
    
    assert b'Alert Added' in response.data

def test_alerts_page_loads(client, auth):
    """Test that alerts page loads with auth"""
    auth.register()
    auth.login()
    
    response = client.get('/linkup/network', follow_redirects=True)
    assert b'Network Management' in response.data