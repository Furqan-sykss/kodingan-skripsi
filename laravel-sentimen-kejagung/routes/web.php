<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\Admin\ResultController;
use App\Http\Controllers\Admin\ScrapeController;
use App\Http\Controllers\Admin\MLAnalysisController;
use App\Http\Controllers\Auth\RegisteredUserController;;

use App\Http\Controllers\ExportController;
use App\Http\Middleware\AdminMiddleware; // ⬅️ Tambahkan ini

// Route::get('/', function () {
//     return view('dashboard');
// })
Route::get('/register', [RegisteredUserController::class, 'create'])->middleware('guest')->name('register');
Route::post('/register', [RegisteredUserController::class, 'store'])->middleware('guest');

// Semua route ini hanya bisa diakses jika sudah login
Route::middleware(['auth'])->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');

    // 🏠 Halaman Dashboard untuk semua user
    Route::get('/', [DashboardController::class, 'index'])->name('dashboard');
    Route::get('/export-komentar-ml', [ExportController::class, 'exportKomentarML'])->name('export.komentar.ml');

    Route::middleware([AdminMiddleware::class])->group(function () {
        Route::post('/scrape', [ScrapeController::class, 'scrape'])->name('scrape');
        Route::get('/result', [ResultController::class, 'index'])->name('scraping.result');
        Route::post('/admin/analyze/analisis-ml', [MLAnalysisController::class, 'analyze_ml'])
            ->name('admin.analyze.ml');
    });
});

require __DIR__ . '/auth.php';