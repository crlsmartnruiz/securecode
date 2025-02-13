from main import get_secret
import os

def test():
    secret_name = "prod/clave-prueba" if os.getenv("ENVIRONMENT", "dev") == "prod" else "dev/clave-prueba"
    assert "clave-prueba-dev" == get_secret(secret_name)