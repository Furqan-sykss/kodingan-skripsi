<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class VaderLabelingController extends Controller
{
    // ✅ Halaman utama pelabelan
    public function index()
    {
        // Ambil 100 data hasil VADER yang belum di-label
        $komentar = DB::table('komentar_sentimen_vader')
            ->whereNull('ground_truth_label')
            ->limit(100)
            ->get();

        return view('admin.vader_labeling.index', compact('komentar'));
    }

    // ✅ Proses penyimpanan label manual
    public function update(Request $request)
    {
        $data = $request->all();

        foreach ($data['label'] as $id => $label) {
            DB::table('komentar_sentimen_vader')
                ->where('id', $id)
                ->update(['ground_truth_label' => $label]);
        }

        return redirect()->route('vader.labeling.index')
            ->with('success', '✅ Pelabelan berhasil disimpan!');
    }
}