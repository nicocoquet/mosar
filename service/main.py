"""Point d'entrée ASGI pour Render."""
from service.app import create_app

app = create_app()
