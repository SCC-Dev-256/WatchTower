from flask import Flask, render_template, send_from_directory, abort
from flask_limiter import Limiter
from flask_caching import Cache
from pydantic import BaseModel, ValidationError
import os

app = Flask(__name__)

# Initialize Flask-Limiter for rate limiting
limiter = Limiter(app, key_func=lambda: "global")

# Initialize Flask-Caching with Redis
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

# Pydantic model for input validation
class FileNameModel(BaseModel):
    filename: str

# Route for dashboard with caching
@app.route("/")
@cache.cached(timeout=60)
def dashboard():
    anomaly_directory = "anomalies/"
    try:
        anomaly_files = os.listdir(anomaly_directory)
    except FileNotFoundError:
        anomaly_files = []
    return render_template("dashboard.html", files=anomaly_files)

# Route to download anomalies with rate limiting and input validation
@app.route("/download/<filename>")
@limiter.limit("5 per minute")
def download_file(filename):
    try:
        # Validate filename using Pydantic
        validated_data = FileNameModel(filename=filename)
    except ValidationError as e:
        abort(400, str(e))
    
    if not os.path.exists(os.path.join("anomalies/", validated_data.filename)):
        abort(404, "File not found")
    
    return send_from_directory("anomalies/", validated_data.filename)

if __name__ == "__main__":
    app.run(debug=True)
