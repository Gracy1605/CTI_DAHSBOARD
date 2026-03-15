import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///threats.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Add your AlienVault OTX API key here
    OTX_API_KEY = "86ed340ac305f26bfb2b2096396fe2d4a7d1f3a7a530602d468fc2405f654899"