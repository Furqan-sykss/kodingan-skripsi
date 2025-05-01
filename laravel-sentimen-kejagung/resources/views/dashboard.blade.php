<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            Dashboard
        </h2>
    </x-slot>

    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">

        {{-- Header --}}
        <div class="flex items-center justify-between mb-4">
            <h1 class="text-2xl font-semibold">Dashboard</h1>
            <p class="text-sm text-white">Login sebagai: <strong>{{ Auth::user()->name }}</strong>
                ({{ Auth::user()->role }})</p>
        </div>

        {{-- Jika admin, tampilkan tombol tambahan --}}
        @if (Auth::user()->role === 'admin')
            <div class="mb-6 space-x-2">
                <a href="{{ route('scrape.run') }}" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">🔄
                    Scraping</a>
                <a href="{{ route('labeling.index') }}"
                    class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">📝 Label Manual</a>
            </div>
        @endif

        <div class="flex justify-center">
            <div class="w-[300px] h-[300px] bg-white rounded shadow p-2">
                <canvas id="sentimentChart" width="300" height="300"></canvas>
            </div>
        </div>
        {{-- Dropdown pemilihan jumlah data --}}
        <form method="GET" action="{{ route('dashboard') }}" class="mb-4">
            <label for="limit" class="text-sm mr-2 font-medium text-gray-700">Tampilkan:</label>
            <select name="limit" id="limit" onchange="this.form.submit()" class="border rounded px-2 py-1">
                <option value="100" {{ $limit == 100 ? 'selected' : '' }}>100</option>
                <option value="200" {{ $limit == 200 ? 'selected' : '' }}>200</option>
                <option value="400" {{ $limit == 400 ? 'selected' : '' }}>400</option>
                <option value="600" {{ $limit == 600 ? 'selected' : '' }}>600</option>
                <option value="all" {{ $limit == 'all' ? 'selected' : '' }}>Semua</option>
            </select>
        </form>

        {{-- Tabel komentar --}}
        <div class="overflow-x-auto bg-white shadow rounded-lg">
            <table class="min-w-full table-auto border border-gray-200 text-sm">
                <thead class="bg-gray-100">
                    <tr class="text-left">
                        <th class="px-4 py-2 border">No</th>
                        <th class="px-4 py-2 border">Username</th>
                        <th class="px-4 py-2 border">Komentar</th>
                        <th class="px-4 py-2 border">Tanggal</th>
                        <th class="px-4 py-2 border">Sentimen (VADER)</th>
                        <th class="px-4 py-2 border">Sentimen (IndoBERT)</th>
                        <th class="px-4 py-2 border">Hybrid</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($komentar as $i => $item)
                        <tr class="{{ $loop->even ? 'bg-gray-50' : '' }}">
                            <td class="px-4 py-2 border">{{ $i + 1 }}</td>
                            <td class="px-4 py-2 border">{{ $item->username }}</td>
                            <td class="px-4 py-2 border">{{ $item->comment }}</td>
                            <td class="px-4 py-2 border">{{ $item->date }}</td>
                            <td class="px-4 py-2 border text-center">{{ $item->vader_sentiment }}</td>
                            <td class="px-4 py-2 border text-center">{{ $item->indobert_sentiment }}</td>
                            <td class="px-4 py-2 border text-center font-semibold">
                                @if ($item->hybrid_sentiment === 'positif')
                                    <span class="text-green-600">Positif</span>
                                @elseif($item->hybrid_sentiment === 'negatif')
                                    <span class="text-red-600">Negatif</span>
                                @else
                                    <span class="text-gray-600">Netral</span>
                                @endif
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>

    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const data = {
            labels: ['Positif', 'Netral', 'Negatif'],
            datasets: [{
                label: 'Distribusi Sentimen',
                data: [
                    {{ $sentimentCounts['positif'] ?? 0 }},
                    {{ $sentimentCounts['netral'] ?? 0 }},
                    {{ $sentimentCounts['negatif'] ?? 0 }}
                ],
                backgroundColor: ['#10b981', '#d1d5db', '#ef4444']
            }]
        };

        new Chart(document.getElementById('sentimentChart'), {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</x-app-layout>
