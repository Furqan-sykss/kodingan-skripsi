<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class KomentarSentimenIndobert extends Model
{
    use HasFactory;

    protected $table = 'komentar_sentimen_indobert';

    protected $fillable = [
        'mentah_id',
        'video_id',
        'username',
        'tanggal_komentar',
        'comment',
        'cleaned_comment',
        'indobert_sentiment_label',
        'indobert_confidence_score',
        'processed_at',
    ];

    public $timestamps = false;
}