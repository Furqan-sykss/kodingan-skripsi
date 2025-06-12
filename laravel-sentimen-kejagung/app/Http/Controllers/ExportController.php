<?php

namespace App\Http\Controllers;

use App\Exports\KomentarSentimenMLExport;
use Maatwebsite\Excel\Facades\Excel;

class ExportController extends Controller
{
    public function exportKomentarML()
    {
        $timestamp = now()->format('Ymd_His');
        return Excel::download(new KomentarSentimenMLExport, "komentar_sentimen_ml_{$timestamp}.xlsx");
    }
}