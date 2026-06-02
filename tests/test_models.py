"""Test Fase 2 — verifikasi semua model dan relasinya."""
from datetime import date
from app.models import User, Wallet, Category, Transaction, Budget, SavingsGoal


class TestUser:
    def test_buat_user(self, db):
        """User bisa dibuat dan disimpan ke database."""
        user = User(email="budi@example.com", name="Budi")
        user.set_password("rahasia")
        db.session.add(user)
        db.session.commit()
        assert user.id is not None

    def test_password_hash_tidak_sama_dengan_plaintext(self, db):
        """Password yang disimpan harus berupa hash, bukan teks asli."""
        user = User(email="ani@example.com", name="Ani")
        user.set_password("12345")
        assert user.password_hash != "12345"

    def test_check_password_benar(self, db):
        """check_password harus True untuk password yang tepat."""
        user = User(email="sari@example.com", name="Sari")
        user.set_password("rahasia123")
        assert user.check_password("rahasia123") is True

    def test_check_password_salah(self, db):
        """check_password harus False untuk password yang salah."""
        user = User(email="doni@example.com", name="Doni")
        user.set_password("benar")
        assert user.check_password("salah") is False

    def test_email_unik(self, db, sample_user):
        """Dua user dengan email yang sama tidak boleh ada."""
        import sqlalchemy.exc
        duplikat = User(email="test@example.com", name="Duplikat")
        duplikat.set_password("pass")
        db.session.add(duplikat)
        try:
            db.session.commit()
            assert False, "Seharusnya error email duplikat"
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()


class TestWallet:
    def test_buat_wallet(self, db, sample_user):
        """Wallet bisa dibuat dengan tipe dan saldo awal."""
        wallet = Wallet(user_id=sample_user.id, name="GoPay", type="ewallet", initial_balance=500_000)
        db.session.add(wallet)
        db.session.commit()
        assert wallet.id is not None
        assert wallet.initial_balance == 500_000

    def test_relasi_user_ke_wallet(self, db, sample_user):
        """User.wallets harus menampung wallet yang dimiliki."""
        w = Wallet(user_id=sample_user.id, name="Tunai", type="cash")
        db.session.add(w)
        db.session.commit()
        db.session.refresh(sample_user)
        assert any(x.name == "Tunai" for x in sample_user.wallets)


class TestCategory:
    def test_buat_kategori_income(self, db, sample_user):
        """Kategori income bisa dibuat."""
        cat = Category(user_id=sample_user.id, name="Freelance", kind="income")
        db.session.add(cat)
        db.session.commit()
        assert cat.id is not None
        assert cat.kind == "income"

    def test_buat_kategori_expense(self, db, sample_user):
        """Kategori expense bisa dibuat."""
        cat = Category(user_id=sample_user.id, name="Transportasi", kind="expense")
        db.session.add(cat)
        db.session.commit()
        assert cat.kind == "expense"


class TestTransaction:
    def test_buat_transaksi_income_dengan_kurs(self, db, sample_user, sample_wallet, sample_category_income):
        """Transaksi income harus menyimpan usd_rate_at_date."""
        trx = Transaction(
            user_id=sample_user.id,
            wallet_id=sample_wallet.id,
            category_id=sample_category_income.id,
            amount=5_000_000,
            kind="income",
            date=date(2026, 5, 1),
            usd_rate_at_date=16_000.0,
        )
        db.session.add(trx)
        db.session.commit()
        assert trx.id is not None
        assert trx.usd_rate_at_date == 16_000.0

    def test_buat_transaksi_expense_tanpa_kurs(self, db, sample_user, sample_wallet, sample_category_expense):
        """Transaksi expense boleh tanpa usd_rate_at_date (null)."""
        trx = Transaction(
            user_id=sample_user.id,
            wallet_id=sample_wallet.id,
            category_id=sample_category_expense.id,
            amount=50_000,
            kind="expense",
            date=date(2026, 5, 2),
        )
        db.session.add(trx)
        db.session.commit()
        assert trx.usd_rate_at_date is None

    def test_amount_tersimpan_sebagai_integer(self, db, sample_user, sample_wallet, sample_category_income):
        """Jumlah uang disimpan sebagai integer rupiah (bukan float)."""
        trx = Transaction(
            user_id=sample_user.id,
            wallet_id=sample_wallet.id,
            category_id=sample_category_income.id,
            amount=3_500_000,
            kind="income",
            date=date(2026, 5, 3),
            usd_rate_at_date=15_900.0,
        )
        db.session.add(trx)
        db.session.commit()
        assert isinstance(trx.amount, int)


class TestBudget:
    def test_buat_budget(self, db, sample_user, sample_category_expense):
        """Budget bisa dibuat untuk bulan dan tahun tertentu."""
        budget = Budget(
            user_id=sample_user.id,
            category_id=sample_category_expense.id,
            month=5,
            year=2026,
            limit_amount=2_000_000,
        )
        db.session.add(budget)
        db.session.commit()
        assert budget.id is not None

    def test_budget_unik_per_user_kategori_bulan(self, db, sample_user, sample_category_expense):
        """Tidak boleh ada dua budget untuk user+kategori+bulan+tahun yang sama."""
        import sqlalchemy.exc
        b1 = Budget(user_id=sample_user.id, category_id=sample_category_expense.id,
                    month=6, year=2026, limit_amount=1_000_000)
        b2 = Budget(user_id=sample_user.id, category_id=sample_category_expense.id,
                    month=6, year=2026, limit_amount=2_000_000)
        db.session.add_all([b1, b2])
        try:
            db.session.commit()
            assert False, "Seharusnya error unique constraint"
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()


class TestSavingsGoal:
    def test_buat_goal(self, db, sample_user):
        """SavingsGoal bisa dibuat dengan target dan deadline."""
        goal = SavingsGoal(
            user_id=sample_user.id,
            name="Liburan Bali",
            target_amount=5_000_000,
            saved_amount=1_000_000,
            deadline=date(2026, 12, 31),
        )
        db.session.add(goal)
        db.session.commit()
        assert goal.id is not None

    def test_saved_amount_default_nol(self, db, sample_user):
        """saved_amount default harus 0 jika tidak diisi."""
        goal = SavingsGoal(user_id=sample_user.id, name="Laptop", target_amount=10_000_000)
        db.session.add(goal)
        db.session.commit()
        assert goal.saved_amount == 0

    def test_deadline_boleh_kosong(self, db, sample_user):
        """Deadline bersifat opsional."""
        goal = SavingsGoal(user_id=sample_user.id, name="Dana Darurat", target_amount=20_000_000)
        db.session.add(goal)
        db.session.commit()
        assert goal.deadline is None
