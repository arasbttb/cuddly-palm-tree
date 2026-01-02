import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Testlerden önce veri tabanını oluşturmak ve testlerden sonra temizlemek için kullanılan test düzeneği."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Test sırasında veri tabanı bağlantısı oluşturur ve testten sonra bağlantıyı kapatır."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "'users' tablosu veri tabanında bulunmalıdır."


def test_add_new_user(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Kullanıcı veri tabanına eklenmiş olmalıdır."
def test_wrong_password(setup_database, connection):
    """Yeni bir kullanıcının eklenmesini test eder."""
    add_user('testuser2', 'testuser@example.com', 'password123455')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    result = authenticate_user('testuser2', 'wrongpassword')
    assert not result, "Yanlış şifre ile doğrulama başarısız olmalıdır."



def test_view_users_db(setup_database, connection):
    """Kullanıcı listesinin doğru şekilde görüntülenmesini test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    assert len(users) > 0, "Veri tabanında en az bir kullanıcı bulunmalıdır."


def test_add_existing_user(setup_database, connection):
    """Aynı kullanıcı adıyla ikinci kez ekleme yapılmamalıdır."""
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users;")
    usernames = [row[0] for row in cursor.fetchall()]
    assert len(usernames) == len(set(usernames)), "Users tablosunda aynı username birden fazla olmamalıdır."


def test_authenticate_existing_user(setup_database, connection):
    """Var olan bir kullanıcıyla doğrulama başarılı olmalıdır."""
    cursor = connection.cursor()
    cursor.execute("SELECT username, password FROM users LIMIT 1;")
    user = cursor.fetchone()
    assert user is not None, "Users tablosunda en az bir kullanıcı olmalı."

    username, password = user
    result = authenticate_user(username, password)
    assert result is True, f"Var olan kullanıcı ({username}) doğru şifre ile doğrulanmalıdır."


def test_authenticate_nonexistent_user(setup_database, connection):
    """Var olmayan bir kullanıcıyla doğrulama başarısız olmalıdır."""
    username = "nonexistentuser"
    password = "anypassword"

    cursor = connection.cursor()
    # SQLite'ta parametre bağlama ? ile yapılır
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    assert count == 0, f"{username} zaten tabloda olmamalı."

    result = authenticate_user(username, password)
    assert result is False, "Var olmayan kullanıcı doğrulanmamalıdır."


def test_authenticate_wrong_password(setup_database, connection):
    """Var olan kullanıcı yanlış şifre ile doğrulanmamalıdır."""
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users LIMIT 1;")
    user = cursor.fetchone()
    assert user is not None, "Users tablosunda en az bir kullanıcı olmalı."

    username = user[0]
    wrong_password = "thisiswrong"

    result = authenticate_user(username, wrong_password)
    assert result is False, f"Kullanıcı {username} yanlış şifre ile doğrulanmamalıdır."

# İşte yazabileceğiniz bazı testler:


"""




"""
