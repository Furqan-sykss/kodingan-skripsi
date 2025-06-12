from scraping_komentar_dedup import run_scraping
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
# curl -X POST http://127.0.0.1:5000/scrape
from sentiment_vader import run_vader_analysis
from ml_predict import run_ML_analysis

app = Flask(__name__)
CORS(app)

# Setup Logging
logging.basicConfig(level=logging.DEBUG)
# Path ke script scraping
SCRIPT_PATH = os.path.join(os.getcwd(), 'public',
                           'scripts', 'scraping_komentar_dedup.py')


# ✅ Endpoint untuk menjalankan scraping

@app.route('/scrape', methods=['POST'])
def scrape():
    app.logger.info("📥 Memulai proses scraping dari endpoint /scrape...")
    try:
        total_disimpan = run_scraping()

        if total_disimpan > 0:
            return jsonify({
                'status': 'success',
                'message': f'Scraping berhasil diselesaikan. Total komentar disimpan: {total_disimpan}'
            }), 200
        else:
            return jsonify({
                'status': 'partial',
                'message': 'Tidak ada komentar yang berhasil disimpan. Coba lagi nanti.'
            }), 200

    except Exception as e:
        logging.exception("❌ Terjadi kesalahan saat menjalankan scraping")
        return jsonify({
            'status': 'error',
            'message': f'Scraping gagal: {str(e)}'
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
