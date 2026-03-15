import os
from flask import Flask, render_template
from dotenv import load_dotenv
from routes.recommend_routes import recommend_bp
from routes.compare_routes import compare_bp

load_dotenv()

from routes.chat_routes import chat_bp
from routes.cart_routes import cart_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")


@app.route("/")
def index():
    return render_template("index.html")


app.register_blueprint(chat_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(compare_bp)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)