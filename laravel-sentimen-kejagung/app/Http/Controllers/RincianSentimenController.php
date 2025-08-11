<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class RincianSentimenController extends Controller
{
    public function index(Request $request)
    {
        $keyword = $request->get('keyword', 'korupsi');
        $year = $request->get('year', date('Y'));
        $sentimen = $request->get('sentimen');
        $keywords = ['korupsi', 'kolusi', 'nepotisme', 'kejaksaan agung'];
        $years = [2024, 2025];

        // Query data utama (untuk tabel & pagination)
        $query = DB::table('komentar_sentimen_ml')
            ->where(function($q) use ($keyword) {
                if ($keyword === 'kejaksaan agung') {
                    $q->where('comment', 'like', '%kejaksaan agung%')
                      ->orWhere('comment', 'like', '%kejagung%');
                } else {
                    $q->where('comment', 'like', "%$keyword%");
                }
            })
            ->whereYear('tanggal_komentar', $year);

        if ($sentimen) {
            $query->where('predicted_label', $sentimen);
        }

        $data = $query->orderBy('tanggal_komentar', 'desc')->paginate(10);

        // Data untuk bar chart: jumlah sentimen per tahun
        $sentimen_per_tahun = [];
        foreach ($years as $y) {
            $query = DB::table('komentar_sentimen_ml')
                ->where(function($q) use ($keyword) {
                    if ($keyword === 'kejaksaan agung') {
                        $q->where('comment', 'like', '%kejaksaan agung%')
                          ->orWhere('comment', 'like', '%kejagung%');
                    } else {
                        $q->where('comment', 'like', "%$keyword%");
                    }
                })
                ->whereYear('tanggal_komentar', $y);

            $sentimen_per_tahun[$y] = [
                'positif' => (clone $query)->where('predicted_label', 'positif')->count(),
                'netral'  => (clone $query)->where('predicted_label', 'netral')->count(),
                'negatif' => (clone $query)->where('predicted_label', 'negatif')->count(),
            ];
        }

        return view('rincian_sentimen', compact('data', 'keywords', 'keyword', 'years', 'year', 'sentimen_per_tahun'));
    }
}
