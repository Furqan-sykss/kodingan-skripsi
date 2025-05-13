<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Http;
use Illuminate\Http\Request;

class SentimentController extends Controller
{
    public function analyzeVader()
    {
        try {
            // 🔄 Mengirim permintaan ke Flask API untuk Analisis VADER
            $response = Http::post('http://127.0.0.1:5000/analyze/vader');

            if ($response->successful()) {
                return redirect()->route('scraping.result')
                    ->with('success', '✅ Analisis VADER berhasil dijalankan!');
            } else {
                return redirect()->route('scraping.result')
                    ->with('error', 'Gagal menjalankan Analisis VADER.');
            }
        } catch (\Exception $e) {
            return redirect()->route('scraping.result')
                ->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }

    public function analyzeIndobert()
    {
        try {
            $response = Http::post('http://127.0.0.1:5000/analyze/indobert');

            if ($response->successful()) {
                return redirect()->route('scraping.result')
                    ->with('success', '✅ Analisis IndoBERT berhasil dijalankan!');
            } else {
                return redirect()->route('scraping.result')
                    ->with('error', 'Gagal menjalankan Analisis IndoBERT.');
            }
        } catch (\Exception $e) {
            return redirect()->route('scraping.result')
                ->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }

    public function analyzeHybrid()
    {
        try {
            $response = Http::post('http://127.0.0.1:5000/analyze/hybrid');

            if ($response->successful()) {
                return redirect()->route('scraping.result')
                    ->with('success', '✅ Analisis Hybrid berhasil dijalankan!');
            } else {
                return redirect()->route('scraping.result')
                    ->with('error', 'Gagal menjalankan Analisis Hybrid.');
            }
        } catch (\Exception $e) {
            return redirect()->route('scraping.result')
                ->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }
}