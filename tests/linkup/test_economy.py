from app.models import Service, User
from app.extensions import db

def test_join_gig_economy(client, auth, app):
    """QA: Can a user register a service?"""
    with app.app_context():
        # Create user directly in the database
        user = User(username='testuser', email='testuser@example.com', wallet_balance=0, reputation_points=0)
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Bypass auth fixture and set session directly
    with client.session_transaction() as session:
        session['_user_id'] = str(user_id)
        session['_fresh'] = True

    response = client.post('/linkup/join', data={
        'service_name': 'Kasi Tech Support',
        'category': 'Technology',
        'description': 'I fix laptops.',
        'location_lat': '-26.2309',
        'location_lng': '27.8596'
    }, follow_redirects=False)

    assert response.status_code == 302

    with app.app_context():
        service = Service.query.filter_by(name='Kasi Tech Support').first()
        assert service is not None
        assert service.latitude == -26.2309
