<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ScrapingController extends Controller
{
    public function scrape(Request $request)
    {
        $url = $request->input('url');
        
        // Kirim request ke Flask API
        $response = Http::post('http://127.0.0.1:5000/scrape', [
            'url' => $url
        ]);

        if ($response->successful()) {
            return redirect()->route('scraping.result')
                             ->with('success', 'Scraping berhasil, data disimpan di database!');
        } else {
            return redirect()->back()->with('error', 'Gagal melakukan scraping. Cek kembali URL atau coba lagi.');
        }
    }

    public function result()
    {
        $komentar = DB::table('komentar_mentah')->get();
        return view('result', compact('komentar'));
    }
}
