<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class KomentarSentimenHybrid extends Model
{
    use HasFactory;

    protected $table = 'komentar_sentimen_hybrid';

    protected $fillable = [
        'mentah_id',
        'video_id',
        'username',
        'tanggal_komentar',
        'comment',
        'cleaned_comment_vader',
        'cleaned_comment_indobert',
        'vader_label',
        'vader_score',
        'indobert_label',
        'indobert_score',
        'final_hybrid_label',
        'confidence_average_score',
        'processed_at',
    ];

    public $timestamps = false;
}