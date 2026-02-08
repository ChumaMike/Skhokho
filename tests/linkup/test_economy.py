from app.models import Service

def test_join_gig_economy(client, auth, app):
    """QA: Can a user register a service?"""
    auth.register()
    auth.login()

    response = client.post('/linkup/join', data={
        'service_name': 'Kasi Tech Support',
        'category': 'Technology',
        'description': 'I fix laptops.',
        'location_lat': '-26.2309', 
        'location_lng': '27.8596'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Kasi Tech Support" in response.data

    with app.app_context():
        service = Service.query.filter_by(name='Kasi Tech Support').first()
        assert service is not None
        assert service.latitude == -26.2309