from sqlmodel import create_engine

from app.core.config import settings

print("BEFORE DONE:", settings.SQLALCHEMY_DATABASE_URI.unicode_string())
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI.unicode_string())
