
from main import call_openai_api

def test_call_openai_api():
    response = call_openai_api("Hola")

    print(response)
    assert response == "¡Hola! ¿Cómo puedo ayudarte hoy?"
