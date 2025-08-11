from scraping_komentar_dedup import run_crawling
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
# curl -X POST http://127.0.0.1:5000/scrape
# curl -X POST http://127.0.0.1:5000/analyze/vader
from sentiment_vader import run_vader_analysis
from ml_predict import run_ML_analysis

app = Flask(__name__)
CORS(app)

# Setup Logging
app_logger = logging.getLogger("flask_app")
app_logger.setLevel(logging.DEBUG)

# Cek agar tidak double handler
app.logger.setLevel(logging.DEBUG)
if not app.logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

# Path ke script scraping
SCRIPT_PATH = os.path.join(os.getcwd(), 'public',
                           'scripts', 'scraping_komentar_dedup.py')


# ✅ Endpoint untuk menjalankan scraping

@app.route('/crawling', methods=['POST'])
def crawl():
    app.logger.info("📥 Memulai proses scraping dari endpoint /crawling...")
    try:
        total_disimpan = run_crawling()

        if total_disimpan > 0:
            return jsonify({
                'status': 'success',
                'message': f'Scraping berhasil diselesaikan. Total komentar disimpan: {total_disimpan}',
                'total_saved': total_disimpan
            }), 200
        else:
            return jsonify({
                'status': 'partial',
                'message': 'Tidak ada komentar yang berhasil disimpan. Coba lagi nanti.',
                'total_saved': 0
            }), 200

    except Exception as e:
        logging.exception("❌ Terjadi kesalahan saat menjalankan crawling")
        return jsonify({
            'status': 'error',
            'message': f'Scraping gagal: {str(e)}'
        }), 500


@app.route('/analyze/analisis-ml', methods=['POST'])
def analyze_ml():
    try:
        result = run_ML_analysis()
        return jsonify(result), 200
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
