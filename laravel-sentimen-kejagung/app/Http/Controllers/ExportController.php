<?php

namespace App\Http\Controllers;

use App\Exports\KomentarSentimenMLExport;
use Maatwebsite\Excel\Facades\Excel;
use Illuminate\Support\Facades\Auth;

class ExportController extends Controller
{
    public function exportKomentarML()
    {
        $timestamp = now()->format('Ymd_His');
        $user = Auth::user(); // pastikan pakai facade Auth

        if ($user && $user->role === 'admin') {
            // Kolom untuk admin
            $columns = [
                'video_id',
                'username',
                'comment',
                'tanggal_komentar',
                'cleaned_comment',
                'comment_translate',
                'predicted_label',
                'created_at',
            ];
        } else {
            // Kolom untuk user biasa
            $columns = [
                'video_id',
                'comment',
                'tanggal_komentar',
                'predicted_label',
                'created_at',
            ];
        }

        $export = new KomentarSentimenMLExport($columns);

        return Excel::download($export, "komentar_sentimen_ml_{$timestamp}.xlsx");
    }
}