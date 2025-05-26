<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProfileController;
// use Illuminate\Support\Facades\DB;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\Admin\ResultController;
use App\Http\Controllers\Admin\ScrapeController;
// use App\Http\Controllers\Admin\LabelingController;
// use App\Http\Controllers\Admin\SentimentController;
use App\Http\Controllers\Admin\MLAnalysisController;
// use App\Http\Controllers\Admin\VaderLabelingController;
use App\Http\Middleware\AdminMiddleware; // ⬅️ Tambahkan ini

// Route::get('/', function () {
//     return view('dashboard');
// })

// Semua route ini hanya bisa diakses jika sudah login
Route::middleware(['auth'])->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
    // Route::get('/admin/vader-labeling', [VaderLabelingController::class, 'index'])->name('vader.labeling.index');
    // Route::post('/admin/vader-labeling/update', [VaderLabelingController::class, 'update'])->name('vader.labeling.update');

    // 🏠 Halaman Dashboard untuk semua user
    Route::get('/', [DashboardController::class, 'index'])->name('dashboard');

    Route::middleware([AdminMiddleware::class])->group(function () {
        Route::post('/scrape', [ScrapeController::class, 'scrape'])->name('scrape');
        Route::get('/result', [ResultController::class, 'index'])->name('scraping.result');
        Route::post('/admin/analyze/analisis-ml', [MLAnalysisController::class, 'analyze_ml'])
            ->name('admin.analyze.ml');



        // Route::get('/admin/labeling', [LabelingController::class, 'index'])->name('labeling.index');
        // Route::post('/admin/labeling/update', [LabelingController::class, 'update'])->name('labeling.update');

        // Route::post('/admin/analyze/vader', [SentimentController::class, 'analyzeVader'])->name('admin.analyze.vader');
        // Route::post('/admin/analyze/indobert', [SentimentController::class, 'analyzeIndobert'])->name('admin.analyze.indobert');
        // Route::post('/admin/analyze/hybrid', [SentimentController::class, 'analyzeHybrid'])->name('admin.analyze.hybrid');


        // // 🔐 Route khusus admin (Scraping, Labeling, Analisis)
        // Route::middleware(['admin'])->group(function () {
        //     Route::get('/admin/scrape', [ScrapeController::class, 'run'])->name('scrape.run');
        //     Route::get('/admin/labeling', [LabelingController::class, 'index'])->name('labeling.index');
        //     Route::post('/admin/labeling/update', [LabelingController::class, 'update'])->name('labeling.update');

        // // 🧠 Analisis Sentimen (baru)
        // Route::get('/admin/analyze/vader', [SentimentController::class, 'analyzeVader'])->name('admin.analyze.vader');
        // Route::get('/admin/analyze/indobert', [SentimentController::class, 'analyzeIndobert'])->name('admin.analyze.indobert');
        // Route::get('/admin/analyze/hybrid', [SentimentController::class, 'analyzeHybrid'])->name('admin.analyze.hybrid');
    });
});

require __DIR__ . '/auth.php';