<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Auth;
use Illuminate\Http\Request;
use App\Models\KomentarSentimenHybrid;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    public function index(Request $request)
    {
        $limit = $request->input('limit', 100);

        $komentar = $limit === 'all'
            ? KomentarSentimenHybrid::orderBy('processed_at', 'desc')->get()
            : KomentarSentimenHybrid::orderBy('processed_at', 'desc')->take($limit)->get();

        $sentimentCounts = KomentarSentimenHybrid::selectRaw('final_hybrid_label as label, COUNT(*) as total')
            ->groupBy('final_hybrid_label')
            ->pluck('total', 'label');

        return view('dashboard', compact('komentar', 'limit', 'sentimentCounts'));
    }
}
