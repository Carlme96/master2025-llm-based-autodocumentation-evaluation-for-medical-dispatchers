from .database import SessionLocal
from .config import Settings, load_env


def get_settings():
	load_env()
	return Settings()


# Dependency for DB sessions
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
