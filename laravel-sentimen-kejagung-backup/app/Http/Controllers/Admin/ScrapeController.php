<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ScrapeController extends Controller
{
    public function scrape()
    {
        // Kirim request ke Flask API
        $response = Http::post('http://127.0.0.1:5000/scrape');

        if ($response->successful()) {
            return response()->json(['status' => 'success', 'message' => 'Scraping berhasil!']);
        } else {
            return response()->json(['status' => 'error', 'message' => 'Scraping gagal!']);
        }
    }
}
