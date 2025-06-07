from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os

# ✅ Import file analisis_sentimen
from sentiment_vader import run_vader_analysis
from ml_predict import run_ML_analysis


app = Flask(__name__)
CORS(app)  # <-- Aktifkan CORS di sini

# Path ke script scraping
SCRIPT_PATH = os.path.join(
    os.getcwd(), 'public/scripts/scraping_komentar_dedup.py')


# ✅ Route untuk Scraping
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


# curl -X POST http://127.0.0.1:5000/analyze/vader
@app.route('/analyze/analisis-ml', methods=['POST'])
def analyze_ml():
    try:
        # Menjalankan script sentiment_vader.py secara langsung
        run_ML_analysis()
        return jsonify({"message": "Analisis ML berhasil!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Route untuk Analisis VADER
@app.route('/analyze/vader', methods=['POST'])
def analyze_vader():
    try:
        result = run_vader_analysis()
        return jsonify({
            "status": "success",
            "message": f"Processed {result['processed']} comments, skipped {result['skipped']}",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
# if __name__ == '__main__':
#     # Tambahkan host='0.0.0.0' agar bisa menerima request lebih baik
#     app.run(host='0.0.0.0', port=5000, debug=True)
