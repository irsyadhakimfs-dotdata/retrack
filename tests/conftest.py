"""Fixture bersama untuk semua test ReFinance."""
import pytest
from datetime import date
from app import create_app
from app.extensions import db as _db
from app.models import User, Wallet, Category, Transaction, Budget, SavingsGoal


@pytest.fixture(scope="session")
def app():
    """Buat app dengan TestConfig (SQLite in-memory)."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Berikan sesi db bersih untuk setiap test (rollback sesudahnya)."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Bersihkan semua data antar test agar tidak saling mempengaruhi
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    """Test client Flask."""
    return app.test_client()


@pytest.fixture(autouse=True)
def _bersihkan_cache_login(app):
    """
    Bersihkan cache pengguna Flask-Login (`g._login_user`) sebelum tiap test.

    Fixture `app` sengaja menahan SATU app context untuk seluruh sesi agar database
    SQLite in-memory tetap hidup. Efek sampingnya: Flask-Login menyimpan pengguna di
    `g._login_user` pada context itu, sehingga status login bisa BOCOR antar test
    (mis. test yang seharusnya menolak akses tanpa login malah lolos). Membersihkan
    cache sebelum tiap test menjaga isolasi.
    """
    from flask import g
    g.pop("_login_user", None)
    yield


# --- Fixture data contoh ---

@pytest.fixture
def sample_user(db):
    """Buat satu pengguna contoh."""
    user = User(email="test@example.com", name="Pengguna Uji")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_wallet(db, sample_user):
    """Buat wallet contoh milik sample_user."""
    wallet = Wallet(user_id=sample_user.id, name="BCA", type="bank", initial_balance=1_000_000)
    db.session.add(wallet)
    db.session.commit()
    return wallet


@pytest.fixture
def sample_category_income(db, sample_user):
    """Kategori pemasukan contoh."""
    cat = Category(user_id=sample_user.id, name="Gaji", kind="income")
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture
def sample_category_expense(db, sample_user):
    """Kategori pengeluaran contoh."""
    cat = Category(user_id=sample_user.id, name="Makan", kind="expense")
    db.session.add(cat)
    db.session.commit()
    return cat
