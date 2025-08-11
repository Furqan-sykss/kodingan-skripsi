<x-app-layout>
    <!DOCTYPE html>
    <html lang="id">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rincian Sentimen Komentar</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .comment-tooltip {
                position: relative;
                display: inline-block;
                max-width: 300px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                cursor: pointer;
            }

            .comment-tooltip::after {
                content: attr(data-comment);
                position: absolute;
                bottom: 125%;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                color: #333;
                padding: 10px;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 100;
                width: max-content;
                max-width: 400px;
                white-space: normal;
                display: none;
                font-size: 14px;
                line-height: 1.4;
                border: 1px solid #e5e7eb;
            }

            .comment-tooltip:hover::after {
                display: block;
            }

            .pagination .pagination-item {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                height: 36px;
                min-width: 36px;
                margin: 0 2px;
                padding: 0 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                color: #4b5563;
                background-color: #f3f4f6;
                transition: all 0.2s ease;
            }

            .pagination .pagination-item:hover:not(.disabled) {
                background-color: #e5e7eb;
            }

            .pagination .pagination-item.active {
                background-color: #3b82f6;
                color: white;
            }

            .pagination .pagination-item.disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .sentiment-badge {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 600;
                text-align: center;
            }

            .sentiment-positif {
                background-color: #dcfce7;
                color: #166534;
            }

            .sentiment-netral {
                background-color: #f3f4f6;
                color: #4b5563;
            }

            .sentiment-negatif {
                background-color: #fee2e2;
                color: #b91c1c;
            }

            .year-selector {
                display: flex;
                gap: 8px;
                margin-bottom: 16px;
            }

            .year-button {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid #d1d5db;
                background-color: white;
            }

            .year-button.active {
                background-color: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }

            @media (max-width: 768px) {
                .comment-tooltip {
                    max-width: 150px;
                }

                .table-responsive {
                    overflow-x: auto;
                    width: 100%;
                }

                .filter-form {
                    flex-direction: column;
                }

                .year-selector {
                    flex-wrap: wrap;
                }
            }
        </style>
    </head>

    <body class="bg-gray-50">
        <div class="max-w-7xl mx-auto py-8 px-4">
            <div class="bg-white rounded-xl shadow-md p-6 mb-8">
                <h2 class="text-2xl font-bold text-gray-800 mb-1">Rincian Sentimen Komentar</h2>
                <p class="text-gray-600 mb-6">Analisis sentimen komentar berdasarkan kata kunci dan tahun</p>

                <form method="GET" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-2">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Kata Kunci</label>
                        <select name="keyword"
                            class="w-full border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 px-4 py-2.5">
                            @foreach ($keywords as $k)
                                <option value="{{ $k }}" @if ($k == $keyword) selected @endif>
                                    {{ ucfirst($k) }}
                                </option>
                            @endforeach
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Tahun</label>
                        <select name="year"
                            class="w-full border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 px-4 py-2.5">
                            @foreach ($years as $y)
                                <option value="{{ $y }}" @if ($y == $year) selected @endif>
                                    {{ $y }}
                                </option>
                            @endforeach
                        </select>
                    </div>

                    <div class="flex items-end">
                        <button type="submit"
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2.5 rounded-lg shadow transition-colors duration-300">
                            Tampilkan Data
                        </button>
                    </div>

                    <div class="flex items-end">
                        <a href="#"
                            class="w-full bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-semibold px-4 py-2.5 rounded-lg shadow text-center transition-colors duration-300">
                            Ekspor Data
                        </a>
                    </div>
                </form>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div class="bg-white rounded-xl shadow-md p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="font-semibold text-lg text-gray-700">Perbandingan Sentimen per Tahun</h3>
                        <div class="flex items-center">
                            <div class="flex items-center mr-4">
                                <div class="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
                                <span class="text-xs text-gray-600">Positif</span>
                            </div>
                            <div class="flex items-center mr-4">
                                <div class="w-3 h-3 bg-gray-400 rounded-full mr-1"></div>
                                <span class="text-xs text-gray-600">Netral</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-3 h-3 bg-red-500 rounded-full mr-1"></div>
                                <span class="text-xs text-gray-600">Negatif</span>
                            </div>
                        </div>
                    </div>
                    <div class="w-full h-[300px]">
                        <canvas id="barchart"></canvas>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-md p-6">
                    <h3 class="font-semibold text-lg text-gray-700 mb-4">Statistik Sentimen</h3>

                    <div class="year-selector">
                        @foreach ($years as $y)
                            <button class="year-button @if ($y == $year) active @endif"
                                data-year="{{ $y }}">
                                {{ $y }}
                            </button>
                        @endforeach
                    </div>

                    <div class="flex gap-4">
                        @foreach ($years as $y)
                            <div class="year-stats w-full" id="stats-{{ $y }}"
                                @if ($y != $year) style="display: none;" @endif>
                                <div class="flex flex-row gap-4">
                                    @php
                                        $dataTahun = $sentimen_per_tahun[$y] ?? [
                                            'positif' => 0,
                                            'netral' => 0,
                                            'negatif' => 0,
                                        ];
                                        $total = $dataTahun['positif'] + $dataTahun['netral'] + $dataTahun['negatif'];
                                        $persen_positif =
                                            $total > 0 ? round(($dataTahun['positif'] / $total) * 100, 1) : 0;
                                        $persen_netral =
                                            $total > 0 ? round(($dataTahun['netral'] / $total) * 100, 1) : 0;
                                        $persen_negatif =
                                            $total > 0 ? round(($dataTahun['negatif'] / $total) * 100, 1) : 0;
                                    @endphp

                                    <div class="bg-green-50 rounded-lg p-5 border border-green-100 flex-1">
                                        <div class="text-3xl font-bold text-green-800 mb-1">{{ $dataTahun['positif'] }}
                                        </div>
                                        <div class="text-sm text-green-600">Komentar Positif</div>
                                        <div class="h-2 bg-green-100 rounded-full mt-3">
                                            <div class="h-full bg-green-500 rounded-full"
                                                style="width: {{ $persen_positif }}%"></div>
                                        </div>
                                        <div class="text-xs text-green-700 mt-1">{{ $persen_positif }}% dari total
                                        </div>
                                    </div>

                                    <div class="bg-gray-50 rounded-lg p-5 border border-gray-200 flex-1">
                                        <div class="text-3xl font-bold text-gray-700 mb-1">{{ $dataTahun['netral'] }}
                                        </div>
                                        <div class="text-sm text-gray-600">Komentar Netral</div>
                                        <div class="h-2 bg-gray-200 rounded-full mt-3">
                                            <div class="h-full bg-gray-500 rounded-full"
                                                style="width: {{ $persen_netral }}%"></div>
                                        </div>
                                        <div class="text-xs text-gray-700 mt-1">{{ $persen_netral }}% dari total
                                        </div>
                                    </div>

                                    <div class="bg-red-50 rounded-lg p-5 border border-red-100 flex-1">
                                        <div class="text-3xl font-bold text-red-800 mb-1">{{ $dataTahun['negatif'] }}
                                        </div>
                                        <div class="text-sm text-red-600">Komentar Negatif</div>
                                        <div class="h-2 bg-red-100 rounded-full mt-3">
                                            <div class="h-full bg-red-500 rounded-full"
                                                style="width: {{ $persen_negatif }}%"></div>
                                        </div>
                                        <div class="text-xs text-red-700 mt-1">{{ $persen_negatif }}% dari total
                                        </div>
                                    </div>
                                </div>
                            </div>
                        @endforeach
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200">
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center">
                        <div>
                            <h3 class="font-semibold text-lg text-gray-700">Data Komentar</h3>
                            <p class="text-gray-500 text-sm mt-1">
                                @if ($data->total() > 0)
                                    Menampilkan {{ $data->firstItem() }} - {{ $data->lastItem() }} dari
                                    {{ $data->total() }} komentar
                                @else
                                    Tidak ada data komentar
                                @endif
                            </p>
                        </div>
                        @if ($data->total() > 0)
                            <div class="mt-2 md:mt-0">
                                <span class="text-sm text-gray-500 mr-2">Filter Sentimen:</span>
                                <div class="inline-flex rounded-md shadow-sm" role="group">
                                    <a href="{{ route('rincian.sentimen', array_merge(request()->except('page'), ['sentimen' => null])) }}"
                                        class="px-3 py-1.5 text-xs font-medium {{ request('sentimen') == null ? 'bg-blue-600 text-white' : 'bg-white text-gray-900' }} border border-gray-200 rounded-l-lg hover:bg-gray-100">
                                        Semua
                                    </a>
                                    <a href="{{ route('rincian.sentimen', array_merge(request()->except('page'), ['sentimen' => 'positif'])) }}"
                                        class="px-3 py-1.5 text-xs font-medium {{ request('sentimen') == 'positif' ? 'bg-green-600 text-white' : 'bg-green-50 text-green-700' }} border-t border-b border-green-200 hover:bg-green-100">
                                        Positif
                                    </a>
                                    <a href="{{ route('rincian.sentimen', array_merge(request()->except('page'), ['sentimen' => 'netral'])) }}"
                                        class="px-3 py-1.5 text-xs font-medium {{ request('sentimen') == 'netral' ? 'bg-gray-600 text-white' : 'bg-gray-50 text-gray-700' }} border-t border-b border-gray-200 hover:bg-gray-100">
                                        Netral
                                    </a>
                                    <a href="{{ route('rincian.sentimen', array_merge(request()->except('page'), ['sentimen' => 'negatif'])) }}"
                                        class="px-3 py-1.5 text-xs font-medium {{ request('sentimen') == 'negatif' ? 'bg-red-600 text-white' : 'bg-red-50 text-red-700' }} border border-red-200 rounded-r-md hover:bg-red-100">
                                        Negatif
                                    </a>
                                </div>
                            </div>
                        @endif
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    No</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Video ID</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Username</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Tanggal Komentar</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Komentar</th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Sentimen</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            @if ($data->isEmpty())
                                <tr>
                                    <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                                        <div class="flex flex-col items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg"
                                                class="h-16 w-16 text-gray-300 mb-3" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <p class="text-lg font-medium text-gray-500">Maaf, Saat ini Data Belum
                                                Tersedia</p>
                                            <p class="text-gray-400 mt-1">Coba gunakan kata kunci atau tahun yang
                                                berbeda</p>
                                        </div>
                                    </td>
                                </tr>
                            @else
                                @foreach ($data as $index => $item)
                                    <tr class="hover:bg-gray-50 transition-colors">
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ ($data->currentPage() - 1) * $data->perPage() + $loop->iteration }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <span
                                                class="font-mono bg-gray-100 px-2 py-1 rounded">{{ $item->video_id }}</span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <div class="flex items-center">
                                                <div
                                                    class="flex-shrink-0 h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-800 font-medium mr-2">
                                                    {{ substr($item->username, 0, 1) }}
                                                </div>
                                                <div>{{ $item->username }}</div>
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ $item->tanggal_komentar }}
                                        </td>
                                        <td class="px-6 py-4 text-sm text-gray-900 max-w-xs">
                                            <div class="comment-tooltip" data-comment="{{ $item->comment }}">
                                                {{ $item->comment }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            @if ($item->predicted_label === 'positif')
                                                <span class="sentiment-badge sentiment-positif">Positif</span>
                                            @elseif($item->predicted_label === 'negatif')
                                                <span class="sentiment-badge sentiment-negatif">Negatif</span>
                                            @elseif($item->predicted_label === 'netral')
                                                <span class="sentiment-badge sentiment-netral">Netral</span>
                                            @else
                                                <span class="text-gray-400">-</span>
                                            @endif
                                        </td>
                                    </tr>
                                @endforeach
                            @endif
                        </tbody>
                    </table>
                </div>

                @if (!$data->isEmpty())
                    <div class="px-6 py-4 border-t border-gray-200">
                        <div class="pagination flex flex-col sm:flex-row items-center justify-between">
                            <div class="text-sm text-gray-700 mb-4 sm:mb-0">
                                Menampilkan {{ $data->firstItem() }} hingga {{ $data->lastItem() }} dari
                                {{ $data->total() }} hasil
                            </div>
                            <div class="flex space-x-1">
                                @if ($data->onFirstPage())
                                    <span class="pagination-item disabled">
                                        &laquo; Sebelumnya
                                    </span>
                                @else
                                    <a href="{{ $data->previousPageUrl() }}" class="pagination-item">
                                        &laquo; Sebelumnya
                                    </a>
                                @endif

                                @foreach ($data->getUrlRange(1, $data->lastPage()) as $page => $url)
                                    @if ($page == $data->currentPage())
                                        <span class="pagination-item active">{{ $page }}</span>
                                    @else
                                        <a href="{{ $url }}"
                                            class="pagination-item">{{ $page }}</a>
                                    @endif
                                @endforeach

                                @if ($data->hasMorePages())
                                    <a href="{{ $data->nextPageUrl() }}" class="pagination-item">
                                        Selanjutnya &raquo;
                                    </a>
                                @else
                                    <span class="pagination-item disabled">
                                        Selanjutnya &raquo;
                                    </span>
                                @endif
                            </div>
                        </div>
                    </div>
                @endif
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Grafik perbandingan sentimen
                const ctx = document.getElementById('barchart').getContext('2d');
                const data = {
                    labels: @json($years),
                    datasets: [{
                            label: 'Positif',
                            data: @json(array_column($sentimen_per_tahun, 'positif')),
                            backgroundColor: '#10b981',
                            borderColor: '#047857',
                            borderWidth: 1
                        },
                        {
                            label: 'Netral',
                            data: @json(array_column($sentimen_per_tahun, 'netral')),
                            backgroundColor: '#9ca3af',
                            borderColor: '#6b7280',
                            borderWidth: 1
                        },
                        {
                            label: 'Negatif',
                            data: @json(array_column($sentimen_per_tahun, 'negatif')),
                            backgroundColor: '#ef4444',
                            borderColor: '#b91c1c',
                            borderWidth: 1
                        }
                    ]
                };

                const config = {
                    type: 'bar',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false
                            }
                        },
                        scales: {
                            x: {
                                stacked: true,
                                grid: {
                                    display: false
                                }
                            },
                            y: {
                                stacked: true,
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }
                            }
                        },
                        interaction: {
                            mode: 'nearest',
                            axis: 'x',
                            intersect: false
                        }
                    }
                };

                new Chart(ctx, config);

                // Fungsi untuk mengganti statistik berdasarkan tahun
                const yearButtons = document.querySelectorAll('.year-button');
                const yearStats = document.querySelectorAll('.year-stats');

                yearButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const selectedYear = this.getAttribute('data-year');

                        // Update active button
                        yearButtons.forEach(btn => btn.classList.remove('active'));
                        this.classList.add('active');

                        // Update year in form
                        document.querySelector('select[name="year"]').value = selectedYear;

                        // Show selected year stats
                        yearStats.forEach(stats => {
                            if (stats.id === `stats-${selectedYear}`) {
                                stats.style.display = 'grid';
                            } else {
                                stats.style.display = 'none';
                            }
                        });
                    });
                });
            });
        </script>
    </body>

    </html>

</x-app-layout>
