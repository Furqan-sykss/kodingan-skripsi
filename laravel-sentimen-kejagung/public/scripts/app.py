from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import traceback
import logging
# curl -X POST http://127.0.0.1:5000/scrape
from sentiment_vader import run_vader_analysis
from ml_predict import run_ML_analysis

app = Flask(__name__)
CORS(app)

# Setup Logging
logging.basicConfig(
    filename='flask_log.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
# Path ke script scraping
SCRIPT_PATH = os.path.join(os.getcwd(), 'public',
                           'scripts', 'scraping_komentar_dedup.py')


# ✅ Endpoint untuk menjalankan scraping
@app.route('/scrape', methods=['POST'])
@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        logging.info("📥 Memulai proses scraping dari endpoint /scrape...")
        result = subprocess.run(
            ['python', SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"❌ Scraping gagal: {result.stderr}")
            return jsonify({
                'status': 'error',
                'message': f"Scraping gagal: {result.stderr}"
            }), 500

        logging.info("✅ Scraping berhasil diselesaikan.")
        return jsonify({
            'status': 'success',
            'message': 'Scraping berhasil diselesaikan.'
        }), 200

    except Exception as e:
        logging.error("❌ Exception saat scraping: " + traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f"Gagal menjalankan scraping: {str(e)}"
        }), 500


@app.route('/analyze/analisis-ml', methods=['POST'])
def analyze_ml():
    try:
        run_ML_analysis()
        return jsonify({"message": "Analisis ML berhasil!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
