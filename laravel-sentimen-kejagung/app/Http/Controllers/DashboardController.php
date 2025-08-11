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
    public function deleteKomentarML($id)
    {
        // Cari data komentar_sentimen_ml
        $komentar = KomentarSentimenML::findOrFail($id);

        // Simpan mentah_id sebelum hapus
        $mentahId = $komentar->mentah_id;

        // Hapus data komentar_sentimen_ml
        $komentar->delete();

        // Hapus data terkait di komentar_mentah
        DB::table('komentar_mentah')->where('id', $mentahId)->delete();

        return response()->json(['success' => true]);
    }
}