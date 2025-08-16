from flask import Flask
import os
from app import create_label_app

# We create the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

label_app = create_label_app(app)

@app.route("/")
def index():
    return label_app.index()

@app.route('/home')
def home():
    """
    Main route where the data is generated and passed to the Dash callback.
    """
    return label_app.index()


@app.route('/custom_dash', methods=['GET'])
def custom_dash():
    return label_app.index()
        

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))