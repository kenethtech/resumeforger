

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 302

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_signup_page(client):
    response = client.get('/signup')
    assert response.status_code == 200

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200

def test_contact_page(client):
    response = client.get('/contact')
    assert response.status_code == 200

