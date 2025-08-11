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
    public function deleteKomentarMentah($id)
    {
        try {
            $komentar = DB::table('komentar_mentah')->where('id', $id)->first();

            if (!$komentar) {
                return response()->json(['success' => false, 'message' => 'Data tidak ditemukan.']);
            }

            // Cek status proses
            $isVader = $komentar->is_processed_vader == 1;
            $isML = $komentar->is_processed_ml == 1;

            // Jika sudah diproses VADER, hapus dulu di komentar_sentimen_vader
            if ($isVader) {
                DB::table('komentar_sentimen_vader')->where('mentah_id', $id)->delete();
            }
            // Jika sudah diproses ML, hapus dulu di komentar_sentimen_ml
            if ($isML) {
                DB::table('komentar_sentimen_ml')->where('mentah_id', $id)->delete();
            }

            // Hapus data utama di komentar_mentah
            DB::table('komentar_mentah')->where('id', $id)->delete();

            return response()->json(['success' => true]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}