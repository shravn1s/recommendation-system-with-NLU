import os
from flask import Flask, render_template
from dotenv import load_dotenv

# -------- LOAD ENV --------
load_dotenv()

# -------- IMPORT SERVICES --------
from services.ai_service import normalized_products
from services.rag_engine import init_rag

# -------- INIT RAG WITH NEW DATA --------
init_rag(normalized_products)

# -------- IMPORT ROUTES --------
from routes.chat_routes import chat_bp
from routes.cart_routes import cart_bp
from routes.recommend_routes import recommend_bp
from routes.compare_routes import compare_bp

# -------- APP INIT --------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")


# -------- ROUTES --------
@app.route("/")
def index():
    return render_template("index.html")


# -------- REGISTER BLUEPRINTS --------
app.register_blueprint(chat_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(compare_bp)


# -------- RUN --------
if __name__ == "__main__":
    app.run(debug=True)
