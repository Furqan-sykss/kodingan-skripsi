<x-app-layout>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <style>
        /* Modern Loading Overlay */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            display: none;
            backdrop-filter: blur(3px);
        }

        .loading-content {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 90%;
            animation: fadeIn 0.3s ease-out;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            margin: 0 auto 1.5rem;
            position: relative;
        }

        .spinner-circle {
            position: absolute;
            width: 100%;
            height: 100%;
            border: 5px solid transparent;
            border-radius: 50%;
            animation: rotate 1.5s linear infinite;
        }

        .spinner-circle-1 {
            border-top-color: #4f46e5;
            border-bottom-color: #4f46e5;
        }

        .spinner-circle-2 {
            border-left-color: #10b981;
            border-right-color: #10b981;
            animation-delay: 0.2s;
        }

        .loading-text {
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .loading-subtext {
            font-size: 0.9rem;
            color: #666;
            line-height: 1.5;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background-color: #f3f4f6;
            border-radius: 3px;
            margin-top: 1rem;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            border-radius: 3px;
            transition: width 0.3s ease;
        }

        @keyframes rotate {
            0% {
                transform: rotate(0deg);
            }

            100% {
                transform: rotate(360deg);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Existing Dashboard Styles */
        .card {
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .dashboard-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            color: white;
        }

        .sentiment-stats-card {
            background: white;
            border-radius: 0.75rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .sentiment-stats-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .sentiment-stats-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }

        .sentiment-stats-total {
            background-color: #f3f4f6;
            color: #4f46e5;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
        }

        .sentiment-stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }

        .sentiment-stat {
            padding: 1rem;
            border-radius: 0.5rem;
            display: flex;
            flex-direction: column;
        }

        .stat-total {
            background-color: #f0f5ff;
            border-left: 4px solid #4f46e5;
        }

        .stat-positif {
            background-color: #f0fdf4;
            border-left: 4px solid #10b981;
        }

        .stat-netral {
            background-color: #f9fafb;
            border-left: 4px solid #9ca3af;
        }

        .stat-negatif {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
        }

        .stat-label {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #111827;
        }

        .stat-percentage {
            font-size: 0.875rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }

        .stat-icon {
            width: 1.25rem;
            height: 1.25rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .icon-total {
            background-color: #e0e7ff;
            color: #4f46e5;
        }

        .icon-positif {
            background-color: #d1fae5;
            color: #10b981;
        }

        .icon-netral {
            background-color: #e5e7eb;
            color: #6b7280;
        }

        .icon-negatif {
            background-color: #fee2e2;
            color: #ef4444;
        }

        .table-container {
            overflow-x: auto;
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        table {
            min-width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }

        th {
            background-color: #f9fafb;
            color: #374151;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        td {
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            color: #4b5563;
        }

        tr:hover td {
            background-color: #f9fafb;
        }

        .sentiment-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: capitalize;
        }

        .sentiment-positif {
            background-color: #d1fae5;
            color: #065f46;
        }

        .sentiment-netral {
            background-color: #e5e7eb;
            color: #374151;
        }

        .sentiment-negatif {
            background-color: #fee2e2;
            color: #991b1b;
        }

        .pagination {
            display: flex;
            justify-content: center;
            padding: 1rem;
        }

        .pagination .page-item {
            margin: 0 0.25rem;
        }

        .pagination .page-link {
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            border: 1px solid #e5e7eb;
            color: #4f46e5;
        }

        .pagination .page-item.active .page-link {
            background-color: #4f46e5;
            color: white;
            border-color: #4f46e5;
        }

        .btn {
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background-color: #4f46e5;
            color: white;
        }

        .btn-primary:hover {
            background-color: #4338ca;
        }

        .btn-success {
            background-color: #10b981;
            color: white;
        }

        .btn-success:hover {
            background-color: #0d9f6e;
        }
    </style>

    <!-- Loading Overlay -->
    <div id="loadingOverlay" class="loading-overlay">
        <div class="loading-content">
            <div class="loading-spinner">
                <div class="spinner-circle spinner-circle-1"></div>
                <div class="spinner-circle spinner-circle-2"></div>
            </div>
            <div class="loading-text" id="loadingText">Memproses Data</div>
            <div class="loading-subtext" id="loadingSubtext">Harap tunggu, proses sedang berjalan...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
    </div>

    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-2xl font-bold">Dashboard Analisis Sentimen</h1>
                    <p class="text-sm opacity-90">Visualisasi hasil analisis sentimen menggunakan Machine Learning</p>
                </div>
                <div class="text-right">
                    <p class="text-sm">Login sebagai:</p>
                    <p class="font-semibold">{{ Auth::user()->name }} <span
                            class="text-xs opacity-80">({{ Auth::user()->role }})</span></p>
                </div>
            </div>
        </div>

        <!-- Sentiment Stats Card -->
        <div class="sentiment-stats-card">
            <div class="sentiment-stats-header">
                <h2 class="sentiment-stats-title">Statistik Sentimen</h2>
                <span class="sentiment-stats-total">Total: {{ $totalData }}</span>
            </div>

            <div class="sentiment-stats-grid">
                <!-- Total Comments -->
                <div class="sentiment-stat stat-total">
                    <span class="stat-label">
                        <span class="stat-icon icon-total">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                                <path fill-rule="evenodd"
                                    d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                                    clip-rule="evenodd" />
                            </svg>
                        </span>
                        Total Komentar
                    </span>
                    <span class="stat-value">{{ $totalData }}</span>
                </div>

                <!-- Positive Comments -->
                <div class="sentiment-stat stat-positif">
                    <span class="stat-label">
                        <span class="stat-icon icon-positif">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                                    clip-rule="evenodd" />
                            </svg>
                        </span>
                        Positif
                    </span>
                    <span class="stat-value">{{ $sentimentCounts['positif'] ?? 0 }}</span>
                    <span class="stat-percentage">
                        {{ $totalData > 0 ? round((($sentimentCounts['positif'] ?? 0) / $totalData) * 100, 1) : 0 }}%
                    </span>
                </div>

                <!-- Neutral Comments -->
                <div class="sentiment-stat stat-netral">
                    <span class="stat-label">
                        <span class="stat-icon icon-netral">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-7.536 5.879a1 1 0 001.415 0 3 3 0 014.242 0 1 1 0 001.415-1.415 5 5 0 00-7.072 0 1 1 0 000 1.415z"
                                    clip-rule="evenodd" />
                            </svg>
                        </span>
                        Netral
                    </span>
                    <span class="stat-value">{{ $sentimentCounts['netral'] ?? 0 }}</span>
                    <span class="stat-percentage">
                        {{ $totalData > 0 ? round((($sentimentCounts['netral'] ?? 0) / $totalData) * 100, 1) : 0 }}%
                    </span>
                </div>

                <!-- Negative Comments -->
                <div class="sentiment-stat stat-negatif">
                    <span class="stat-label">
                        <span class="stat-icon icon-negatif">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-7.536 5.879a1 1 0 001.415 0 3 3 0 014.242 0 1 1 0 001.415-1.415 5 5 0 00-7.072 0 1 1 0 000 1.415z"
                                    clip-rule="evenodd" />
                            </svg>
                        </span>
                        Negatif
                    </span>
                    <span class="stat-value">{{ $sentimentCounts['negatif'] ?? 0 }}</span>
                    <span class="stat-percentage">
                        {{ $totalData > 0 ? round((($sentimentCounts['negatif'] ?? 0) / $totalData) * 100, 1) : 0 }}%
                    </span>
                </div>
            </div>
        </div>

        <!-- Admin Tools -->
        @if (Auth::user()->role === 'admin')
            <div class="card mb-6">
                <h2 class="text-lg font-semibold mb-4 text-gray-800">Admin Tools</h2>
                <div class="flex flex-wrap gap-3">
                    <!-- Scrape Button -->
                    <button id="scrapeButton" class="btn btn-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                                clip-rule="evenodd" />
                        </svg>
                        Scraping Data
                    </button>

                    <!-- ML Analysis Button -->
                    <form id="ml-form" action="{{ route('admin.analyze.ml') }}" method="POST" class="m-0">
                        @csrf
                        <button id="btn-analisis-ml" class="btn btn-success">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                                    clip-rule="evenodd" />
                            </svg>
                            Analisis ML
                        </button>
                    </form>
                </div>
            </div>
        @endif

        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div class="card">
                <h2 class="text-lg font-semibold mb-4 text-gray-800">Distribusi Sentimen</h2>
                <div class="w-full h-64">
                    <canvas id="sentimentChart" width="100%" height="100%"></canvas>
                </div>
            </div>

            <div class="card">
                <h2 class="text-lg font-semibold mb-4 text-gray-800">Detail Sentimen</h2>
                <div class="space-y-3">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <div class="w-3 h-3 rounded-full bg-green-500"></div>
                            <span>Positif</span>
                        </div>
                        <span class="font-medium">{{ $sentimentCounts['positif'] ?? 0 }}
                            ({{ $totalData > 0 ? round((($sentimentCounts['positif'] ?? 0) / $totalData) * 100, 1) : 0 }}%)</span>
                    </div>

                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <div class="w-3 h-3 rounded-full bg-gray-400"></div>
                            <span>Netral</span>
                        </div>
                        <span class="font-medium">{{ $sentimentCounts['netral'] ?? 0 }}
                            ({{ $totalData > 0 ? round((($sentimentCounts['netral'] ?? 0) / $totalData) * 100, 1) : 0 }}%)</span>
                    </div>

                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <div class="w-3 h-3 rounded-full bg-red-500"></div>
                            <span>Negatif</span>
                        </div>
                        <span class="font-medium">{{ $sentimentCounts['negatif'] ?? 0 }}
                            ({{ $totalData > 0 ? round((($sentimentCounts['negatif'] ?? 0) / $totalData) * 100, 1) : 0 }}%)</span>
                    </div>

                    <div class="pt-3 mt-3 border-t border-gray-200">
                        <div class="flex items-center justify-between">
                            <span class="font-medium">Total</span>
                            <span class="font-bold">{{ $totalData }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Comments Table -->
        <div class="card !p-0">
            <div class="p-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-800">Data Komentar</h2>
                <p class="text-sm text-gray-600">Hasil analisis sentimen machine learning</p>
            </div>

            <div class="table-container">
                <table class="min-w-full">
                    <thead>
                        <tr>
                            <th class="px-6 py-3">No</th>
                            <th class="px-6 py-3">Username</th>
                            <th class="px-6 py-3">Komentar</th>
                            <th class="px-6 py-3">Tanggal</th>
                            <th class="px-6 py-3">Label ML</th>
                            <th class="px-6 py-3">Confidence</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        @foreach ($komentar as $item)
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ ($komentar->currentPage() - 1) * $komentar->perPage() + $loop->iteration }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                                    {{ $item->username }}
                                </td>
                                <td class="px-6 py-4">
                                    <div class="max-w-xs truncate">{{ $item->comment }}</div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ $item->tanggal_komentar }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    @if ($item->predicted_label === 'positif')
                                        <span class="sentiment-badge sentiment-positif">Positif</span>
                                    @elseif($item->predicted_label === 'negatif')
                                        <span class="sentiment-badge sentiment-negatif">Negatif</span>
                                    @else
                                        <span class="sentiment-badge sentiment-netral">Netral</span>
                                    @endif
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                                        <div class="bg-blue-600 h-2.5 rounded-full"
                                            style="width: {{ $item->confidence_score * 100 }}%"></div>
                                    </div>
                                    <span
                                        class="text-xs text-gray-500 mt-1">{{ number_format($item->confidence_score, 2) }}</span>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>

                <div class="pagination">
                    {{ $komentar->links() }}
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript for Loading Overlay and AJAX -->
    <script>
        // Enhanced Loading Functionality
        function showLoading(message, submessage) {
            $('#loadingText').text(message || 'Memproses Data');
            $('#loadingSubtext').text(submessage || 'Harap tunggu, proses sedang berjalan...');
            $('#progressFill').css('width', '0%');
            $('#loadingOverlay').fadeIn(200);

            // Simulate progress for longer operations
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress > 90) clearInterval(progressInterval);
                $('#progressFill').css('width', `${progress}%`);
            }, 500);
        }

        function hideLoading() {
            $('#loadingOverlay').fadeOut(200);
        }

        // Scraping Process
        $('#scrapeButton').on('click', function() {
            showLoading(
                'Sedang melakukan scraping...',
                'Proses ini mungkin memakan waktu beberapa menit'
            );

            $.ajax({
                url: "http://127.0.0.1:5000/scrape",
                type: "POST",
                headers: {
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                success: function(response) {
                    hideLoading();
                    alert(response.message);
                    if (confirm("Scraping berhasil! Ingin melihat hasil?")) {
                        window.location.href = "{{ route('scraping.result') }}";
                    }
                },
                error: function(xhr, status, error) {
                    hideLoading();
                    alert("Tidak dapat menghubungi server. Error: " + status);
                }
            });
        });

        // ML Analysis Process
        $('#btn-analisis-ml').click(function(event) {
            event.preventDefault();
            if (confirm("Yakin ingin melakukan analisis ML pada 400 data terbaru?")) {
                showLoading(
                    'Sedang menganalisis sentimen...',
                    'Proses machine learning sedang berjalan'
                );

                $.ajax({
                    url: "http://127.0.0.1:5000/analyze/analisis-ml",
                    type: "POST",
                    success: function(response) {
                        hideLoading();
                        alert(response.message);
                        window.location.href = "{{ route('dashboard') }}";
                    },
                    error: function(xhr, status, error) {
                        hideLoading();
                        alert("Terjadi kesalahan saat analisis ML. Error: " + error);
                    }
                });
            }
        });
    </script>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const positif = {{ $sentimentCounts['positif'] ?? 0 }};
        const netral = {{ $sentimentCounts['netral'] ?? 0 }};
        const negatif = {{ $sentimentCounts['negatif'] ?? 0 }};
        const dataPie = (positif === 0 && netral === 0 && negatif === 0) ? [1, 1, 1] : [positif, netral, negatif];

        const data = {
            labels: ['Positif', 'Netral', 'Negatif'],
            datasets: [{
                label: 'Distribusi Sentimen',
                data: dataPie,
                backgroundColor: ['#10b981', '#d1d5db', '#ef4444'],
                borderColor: ['#0d9488', '#9ca3af', '#dc2626'],
                borderWidth: 1,
                hoverOffset: 4
            }]
        };

        const ctx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    </script>
</x-app-layout>
