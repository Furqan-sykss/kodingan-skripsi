<?php

namespace App\Exports;

use App\Models\KomentarSentimenML;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;

class KomentarSentimenMLExport implements FromCollection, WithHeadings
{
    public function collection()
    {
        return KomentarSentimenML::select('video_id', 'tanggal_komentar', 'comment', 'predicted_label', 'created_at')->get();
    }

    public function headings(): array
    {
        return [
            'video_id', 'tanggal_komentar',
            'comment',
            'Label Prediksi',
            'Tanggal Dibuat',
        ];
    }
}