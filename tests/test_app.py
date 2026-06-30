import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, db, Counter
import pytest

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:secret@localhost:5432/counterdb')
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_counter_increment(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    assert 'Visits: 1' in data

    response = client.get('/')
    assert 'Visits: 2' in response.data.decode('utf-8')

def test_db_model():
    with app.app_context():
        counter = Counter.get_counter()
        assert counter.count == 0
        counter.count += 1
        db.session.commit()
        new_counter = Counter.query.first()
        assert new_counter.count == 1