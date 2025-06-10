<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Auth;
use Illuminate\Http\Request;
use App\Models\KomentarSentimenML;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    public function index(Request $request)
    {
        $limit = $request->input('limit', 10);
        $komentar = KomentarSentimenML::orderBy('created_at', 'desc')->paginate($limit);
        $sentimentCounts = KomentarSentimenML::selectRaw('predicted_label as label, COUNT(*) as total')
            ->groupBy('predicted_label')
            ->pluck('total', 'label');
        // 🚀 Ambil Total Data Keseluruhan
        $totalData = KomentarSentimenML::count();
        return view('dashboard', compact('komentar', 'limit', 'sentimentCounts', 'totalData'));
    }
}