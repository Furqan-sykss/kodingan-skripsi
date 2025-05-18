<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\DB;

class MLAnalysisController extends Controller
{
    public function index()
    {
        $data = DB::table('komentar_sentimen_ml')->orderBy('created_at', 'desc')->get();
        return view('admin.ml_analysis', compact('data'));
    }
}