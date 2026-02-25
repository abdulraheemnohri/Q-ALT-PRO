from flask import Flask, render_template
from api.routes import api_bp
from config import Config
import storage # This will initialize the DB

app = Flask(__name__)
app.config.from_object(Config)

# Register API blueprint
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
