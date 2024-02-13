from src import create_app
from src.config import DevelopmentConfig

app = create_app(config=DevelopmentConfig)

if __name__ == "__main__":
    app.run(debug=True)
