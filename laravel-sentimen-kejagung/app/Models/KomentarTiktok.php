<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class KomentarTiktok extends Model
{
    use HasFactory;

    protected $table = 'komentar_tiktok';

    protected $fillable = [
        'video_id',
        'kata_kunci',
        'username',
        'user_id',
        'comment',
        'cleaned_comment',
        'likes',
        'replies',
        'date',
        'vader_sentiment',
        'vader_score',
        'indobert_sentiment',
        'indobert_confidence',
        'hybrid_sentiment',
    ];
}