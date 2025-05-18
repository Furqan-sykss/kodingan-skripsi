from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os

# ✅ Import file analisis_sentimen
from sentiment_vader import run_vader_analysis
from sentiment_indobert import run_indobert_analysis  # ⬅️ Tambahkan ini nanti
from sentiment_hybrid import run_hybrid_analysis  # ⬅️ tambahkan ini


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


@app.route('/api/analyze-ml', methods=['GET'])
def analyze_ml():
    try:
        # Menjalankan script Python untuk prediksi
        result = subprocess.run(
            ['python', 'public/scripts/ml_predict.py'], capture_output=True, text=True
        )

        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": "Proses analisis ML berhasil dijalankan.",
                "output": result.stdout
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Terjadi kesalahan saat menjalankan analisis ML.",
                "output": result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ✅ Route untuk Analisis VADER
@app.route('/analyze/vader', methods=['POST'])
def analyze_vader():
    try:
        # Menjalankan script sentiment_vader.py secara langsung
        run_vader_analysis()
        return jsonify({"message": "Analisis VADER berhasil!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route Baru untuk Analisis IndoBERT


@app.route('/analyze/indobert', methods=['POST'])
def analyze_indobert():
    try:
        run_indobert_analysis()
        return jsonify({"message": "Analisis IndoBERT berhasil!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route baru untuk Analisis Hybrid


@app.route('/analyze/hybrid', methods=['POST'])
def analyze_hybrid():
    try:
        run_hybrid_analysis()
        return jsonify({"message": "Analisis Hybrid berhasil!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
# if __name__ == '__main__':
#     # Tambahkan host='0.0.0.0' agar bisa menerima request lebih baik
#     app.run(host='0.0.0.0', port=5000, debug=True)
