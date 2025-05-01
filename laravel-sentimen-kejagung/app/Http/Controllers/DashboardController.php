<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Auth;
use Illuminate\Http\Request;
use App\Models\KomentarTiktok;

class DashboardController extends Controller
{
    public function index(Request $request)
    {
        $limit = $request->input('limit', 100);

        $komentar = $limit === 'all'
            ? KomentarTiktok::latest()->get()
            : KomentarTiktok::latest()->take($limit)->get();

        $sentimentCounts = KomentarTiktok::selectRaw('hybrid_sentiment, COUNT(*) as total')
            ->groupBy('hybrid_sentiment')
            ->pluck('total', 'hybrid_sentiment');

        return view('dashboard', compact('komentar', 'limit', 'sentimentCounts'));
    }
}