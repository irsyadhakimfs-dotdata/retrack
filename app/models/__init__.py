# Import semua model agar Flask-Migrate bisa mendeteksinya saat membuat migrasi
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.savings_goal import SavingsGoal
# Model investasi emas (ledger terpisah untuk memantau kenaikan nilai)
from app.models.gold_holding import GoldHolding
# Model DWH (star schema) — lapisan Data Warehouse di atas OLTP
from app.models.dwh import DimDate, DimUser, DimWallet, DimCategory, FactTransaction
