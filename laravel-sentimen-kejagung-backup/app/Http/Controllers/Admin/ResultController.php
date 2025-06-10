<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ResultController extends Controller
{
    public function index()
    {
        try {
            // Ambil data dari tabel komentar_mentah
            $komentar = DB::table('komentar_mentah')
                ->orderBy('created_at', 'desc')
                ->paginate(10);

            // Redirect ke view dengan data
            return view('admin.scraping.result', compact('komentar'));
        } catch (\Exception $e) {
            // Jika gagal ambil data, tampilkan pesan error
            return response()->json([
                'error' => $e->getMessage()
            ]);
        }
    }
}