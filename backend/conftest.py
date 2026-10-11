import os

# pytest carga este archivo antes que los tests: toda la suite usa una base en
# memoria y nunca toca database.db
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
