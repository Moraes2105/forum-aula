import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Site_CA import app, database

with app.app_context():
    database.drop_all()
    database.create_all()
