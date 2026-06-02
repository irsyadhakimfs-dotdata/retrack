import os
from app import create_app

# Ambil nama environment dari .env, default ke development
env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    app.run()
