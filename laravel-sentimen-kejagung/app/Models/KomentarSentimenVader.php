<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class KomentarSentimenVader extends Model
{
    use HasFactory;

    protected $table = 'komentar_sentimen_vader';

    protected $fillable = [
        'mentah_id',
        'video_id',
        'username',
        'tanggal_komentar',
        'comment',
        'cleaned_comment',
        'comment_translate',
        'vader_pos',
        'vader_neu',
        'vader_neg',
        'compound_score',
        'label_vader',
        'processed_at',
    ];

    public $timestamps = false;
}