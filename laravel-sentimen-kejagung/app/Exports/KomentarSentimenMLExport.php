<?php

namespace App\Exports;

use App\Models\KomentarSentimenML;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;

class KomentarSentimenMLExport implements FromCollection, WithHeadings
{
    protected $columns;

    public function __construct(array $columns)
    {
        $this->columns = $columns;
    }

    public function collection()
    {
        return KomentarSentimenML::select($this->columns)->get();
    }

    public function headings(): array
    {
        return $this->columns;
    }
}