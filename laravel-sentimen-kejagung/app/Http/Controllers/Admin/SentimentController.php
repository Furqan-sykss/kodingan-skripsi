<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class SentimentController extends Controller
{
    public function analyzeVader()
    {
        $output = shell_exec('python3 sentiment_vader.py');
        return view('admin.feedback', [
            'message' => '✅ Analisis VADER selesai!',
            'next' => route('admin.analyze.indobert'),
            'next_label' => 'Lanjut Analisis IndoBERT'
        ]);
    }

    public function analyzeIndobert()
    {
        $output = shell_exec('python3 sentiment_indobert.py');
        return view('admin.feedback', [
            'message' => '✅ Analisis IndoBERT selesai!',
            'next' => route('admin.analyze.hybrid'),
            'next_label' => 'Lanjut Proses Hybrid'
        ]);
    }

    public function analyzeHybrid()
    {
        $output = shell_exec('python3 sentiment_hybrid.py');
        return view('admin.feedback', [
            'message' => '✅ Analisis Hybrid selesai!',
            'next' => route('dashboard'),
            'next_label' => 'Kembali ke Dashboard'
        ]);
    }
}