"""ubah kolom transactions.date dari Date ke DateTime (tambah komponen waktu)

Revision ID: a1c2f3e4b5d6
Revises: 8df4d27d7c4b
Create Date: 2026-05-31 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1c2f3e4b5d6'
down_revision = '8df4d27d7c4b'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite tidak mendukung ALTER COLUMN langsung → pakai batch (rekonstruksi tabel).
    # Nilai tanggal lama "YYYY-MM-DD" tetap valid sebagai DateTime (jam jadi 00:00:00).
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.alter_column(
            "date",
            existing_type=sa.Date(),
            type_=sa.DateTime(),
            existing_nullable=False,
        )


def downgrade():
    # Kembalikan ke Date (komponen jam akan terpangkas).
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.alter_column(
            "date",
            existing_type=sa.DateTime(),
            type_=sa.Date(),
            existing_nullable=False,
        )
