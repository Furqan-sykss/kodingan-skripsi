<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class KomentarSentimenML extends Model
{
    use HasFactory;

    protected $table = 'komentar_sentimen_ml'; // Nama tabel di database
    protected $primaryKey = 'id'; // Primary key
    public $timestamps = false; // Jika tidak ada created_at dan updated_at

    // Kolom yang bisa diisi secara mass-assignment
    protected $fillable = [
        'mentah_id',
        'video_id',
        'username',
        'comment',
        'tanggal_komentar',
        'cleaned_comment',
        'comment_translate',
        'predicted_label',
        'confidence_score',
        'created_at'
    ];
}