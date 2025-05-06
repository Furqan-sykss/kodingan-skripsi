<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class KomentarMentah extends Model
{
    use HasFactory;

    protected $table = 'komentar_mentah';

    protected $fillable = [
        'video_id',
        'kata_kunci',
        'username',
        'comment',
        'likes',
        'replies',
        'tanggal_komentar',
        'is_processed_vader',
        'is_processed_indobert',
        'created_at',
    ];

    public $timestamps = false;
}