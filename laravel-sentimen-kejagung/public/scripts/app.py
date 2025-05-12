from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # <-- Aktifkan CORS di sini

# Path ke script scraping
SCRIPT_PATH = os.path.join(
    os.getcwd(), 'public/scripts/scraping_komentar_dedup.py')


@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Menjalankan script scraping langsung
        process = subprocess.Popen(
            ['python', SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return jsonify({"error": stderr.decode('utf-8')}), 500

        return jsonify({"message": "Scraping berhasil!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
