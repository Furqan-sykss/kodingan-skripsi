<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;


class MLAnalysisController extends Controller
{
    public function analyze_ml()
    {
        try {
            // 🔄 Mengirim permintaan ke Flask API untuk Analisis VADER
            $response = Http::post('http://127.0.0.1:5000/analyze/analisis-ml');

            if ($response->successful()) {
                return redirect()->route('dashboard')
                    ->with('success', '✅ Analisis ML berhasil dijalankan!');
            } else {
                return redirect()->route('dashboard')
                    ->with('error', 'Gagal menjalankan Analisis ML.');
            }
        } catch (\Exception $e) {
            return redirect()->route('dashboard')
                ->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }
}