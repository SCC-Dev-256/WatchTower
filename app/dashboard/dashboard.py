from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Route for dashboard
@app.route("/")
def dashboard():
    anomaly_directory = "anomalies/"
    anomaly_files = os.listdir(anomaly_directory)
    return render_template("dashboard.html", files=anomaly_files)

# Route to download anomalies
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("anomalies/", filename)

if __name__ == "__main__":
    app.run(debug=True)
