<x-app-layout>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <style>
        #loading {
            display: none;
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">

        {{-- Header --}}
        <div class="flex items-center justify-between mb-4">
            <h1 class="text-2xl text-white font-semibold">Dashboard</h1>
            <p class="text-sm text-white">
                Login sebagai: <strong>{{ Auth::user()->name }}</strong> ({{ Auth::user()->role }})
            </p>
        </div>

        {{-- Tombol Admin --}}
        @if (Auth::user()->role === 'admin')
            <div class="mb-6 space-x-2">

                {{-- Tombol Scrape --}}
                <button id="scrapeButton" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    🔄 Scraping
                </button>
                <img id="loading" src="{{ asset('images/loading.gif') }}" alt="Loading..."
                    style="display:none; margin-left: 10px;">

                {{-- <a href="{{ route('labeling.index') }}"
                    class="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">📝 Label Manual</a> --}}

                {{-- tombol analisis ML --}}
                <button id="btn-analisis-ml" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Analisis ML
                </button>
                <img id="loading" src="{{ asset('images/loading.gif') }}" alt="Loading..."
                    style="display:none; margin-left: 10px;">


                {{-- Tombol VADER --}}
                {{-- <form id="vaderForm" action="{{ route('admin.analyze.vader') }}" method="POST" style="display:inline;">
                    @csrf
                    <button id="vaderButton" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        🧠 Analisis VADER
                    </button>
                    <img id="loadingVader" src="{{ asset('images/loading.gif') }}" alt="Loading..."
                        style="display:none; margin-left: 10px;">
                </form> --}}

                {{-- Tombol IndoBERT --}}
                {{-- <form id="indobertForm" action="{{ route('admin.analyze.indobert') }}" method="POST"
                    style="display:inline;">
                    @csrf
                    <button id="indobertButton" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                        🔍 Analisis IndoBERT
                    </button>
                    <img id="loadingIndobert" src="{{ asset('images/loading.gif') }}" alt="Loading..."
                        style="display:none; margin-left: 10px;">
                </form> --}}

                {{-- Tombol Hybrid --}}
                {{-- <form id="hybridForm" action="{{ route('admin.analyze.hybrid') }}" method="POST"
                    style="display:inline;">
                    @csrf
                    <button id="hybridButton" class="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700">
                        ♻️ Proses Hybrid
                    </button>
                    <img id="loadingHybrid" src="{{ asset('images/loading.gif') }}" alt="Loading..."
                        style="display:none; margin-left: 10px;">
                </form> --}}

            </div>
        @endif

        {{-- Pie Chart --}}
        <div class="flex justify-center mb-6">
            <div class="w-[300px] h-[300px] bg-white rounded shadow p-2">
                <canvas id="sentimentChart" width="300" height="300"></canvas>
            </div>
        </div>

        {{-- Filter jumlah data --}}
        <form method="GET" action="{{ route('dashboard') }}" class="mb-4">
            <label for="limit" class="text-sm mr-2 font-medium text-white">Tampilkan:</label>
            <select name="limit" id="limit" onchange="this.form.submit()" class="border rounded px-2 py-1">
                <option value="100" {{ $limit == 100 ? 'selected' : '' }}>100</option>
                <option value="200" {{ $limit == 200 ? 'selected' : '' }}>200</option>
                <option value="400" {{ $limit == 400 ? 'selected' : '' }}>400</option>
                <option value="600" {{ $limit == 600 ? 'selected' : '' }}>600</option>
                <option value="all" {{ $limit == 'all' ? 'selected' : '' }}>Semua</option>
            </select>

            {{-- Menampilkan Total Data --}}
            <p class="text-sm ml-4 font-medium text-white">
                Total Data: <strong>{{ $totalData }}</strong>
            </p>
        </form>

        {{-- Tabel Komentar ML --}}
        <div class="overflow-x-auto bg-white shadow rounded-lg">
            <table class="min-w-full table-auto border border-gray-200 text-sm">
                <thead class="bg-gray-100">
                    <tr class="text-left">
                        <th class="px-4 py-2 border">No</th>
                        <th class="px-4 py-2 border">Username</th>
                        <th class="px-4 py-2 border">Komentar</th>
                        <th class="px-4 py-2 border">Tanggal</th>
                        <th class="px-4 py-2 border">Label ML</th>
                        <th class="px-4 py-2 border">Confidence Score</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($komentar as $i => $item)
                        <tr class="{{ $loop->even ? 'bg-gray-50' : '' }}">
                            <td class="px-4 py-2 border">{{ $i + 1 }}</td>
                            <td class="px-4 py-2 border">{{ $item->username }}</td>
                            <td class="px-4 py-2 border">{{ $item->comment }}</td>
                            <td class="px-4 py-2 border">{{ $item->tanggal_komentar }}</td>
                            <td class="px-4 py-2 border text-center">
                                @if ($item->predicted_label === 'positif')
                                    <span class="text-green-600">Positif</span>
                                @elseif($item->predicted_label === 'negatif')
                                    <span class="text-red-600">Negatif</span>
                                @else
                                    <span class="text-gray-600">Netral</span>
                                @endif
                            </td>
                            <td class="px-4 py-2 border text-center">{{ number_format($item->confidence_score, 2) }}
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>

    </div>

    {{-- Script AJAX Scraping --}}
    <script>
        $('#scrapeButton').on('click', function() {
            $('#loading').show();
            $.ajax({
                url: "http://127.0.0.1:5000/scrape",
                type: "POST",
                headers: {
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                success: function(response) {
                    $('#loading').hide();
                    alert(response.message);
                    if (confirm("Scraping berhasil! Ingin melihat hasil?")) {
                        window.location.href = "{{ route('scraping.result') }}";
                    }
                },
                error: function(xhr, status, error) {
                    $('#loading').hide();
                    alert("Tidak dapat menghubungi server. Error: " + status);
                }
            });
        });
    </script>


    {{-- Script AJAX analisis sentimen --}}
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js">
        $('#btn-analisis-ml').click(function() {
            if (confirm("Yakin ingin melakukan analisis ML pada 400 data terbaru?")) {
                $.ajax({
                    url: "http://127.0.0.1:5000/api/analyze-ml",
                    type: "GET",
                    success: function(response) {
                        alert(response.message);
                        console.log(response.output);
                        // Refresh halaman untuk memuat hasil terbaru
                        window.location.reload();
                    },
                    error: function(xhr, status, error) {
                        alert("Terjadi kesalahan: " + error);
                        console.error(xhr.responseText);
                    }
                });
            }
        });



        // $('#vaderButton').on('click', function(e) {
        //     e.preventDefault();
        //     $('#loadingVader').show();

        //     $.ajax({
        //         url: "http://127.0.0.1:5000/analyze/vader", // ⬅️ Ganti URL langsung ke Flask
        //         type: "POST",
        //         success: function(response) {
        //             $('#loadingVader').hide();
        //             alert(response.message);
        //             window.location.href = "{{ route('scraping.result') }}";
        //         },
        //         error: function(xhr, status, error) {
        //             $('#loadingVader').hide();
        //             alert("Terjadi kesalahan saat analisis VADER. Error: " + error);
        //         }
        //     });
        // });

        // $('#indobertButton').on('click', function(e) {
        //     e.preventDefault();
        //     $('#loadingIndobert').show();

        //     $.ajax({
        //         url: "http://127.0.0.1:5000/analyze/indobert", // Langsung ke Flask
        //         type: "POST",
        //         success: function(response) {
        //             $('#loadingIndobert').hide();
        //             alert(response.message);
        //             window.location.href = "{{ route('scraping.result') }}";
        //         },
        //         error: function(xhr, status, error) {
        //             $('#loadingIndobert').hide();
        //             alert("Terjadi kesalahan saat analisis IndoBERT: " + error);
        //         }
        //     });
        // });

        // $('#hybridButton').on('click', function(e) {
        //     e.preventDefault();
        //     $('#loadingHybrid').show();

        //     $.ajax({
        //         url: "http://127.0.0.1:5000/analyze/hybrid", // Langsung ke Flask API
        //         type: "POST",
        //         success: function(response) {
        //             $('#loadingHybrid').hide();
        //             alert(response.message);
        //             window.location.href = "{{ route('scraping.result') }}";
        //         },
        //         error: function(xhr, status, error) {
        //             $('#loadingHybrid').hide();
        //             alert("Terjadi kesalahan saat proses Hybrid: " + error);
        //         }
        //     });
        // });
    </script>



    {{-- Chart.js --}}
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Cek apakah datanya ada
        const positif = {{ $sentimentCounts['positif'] ?? 0 }};
        const netral = {{ $sentimentCounts['netral'] ?? 0 }};
        const negatif = {{ $sentimentCounts['negatif'] ?? 0 }};

        // Jika semua data kosong, buat nilai default
        const dataPie = (positif === 0 && netral === 0 && negatif === 0) ? [1, 1, 1] : [positif, netral, negatif];

        // ✅ Data untuk Pie Chart
        const data = {
            labels: ['Positif', 'Netral', 'Negatif'],
            datasets: [{
                label: 'Distribusi Sentimen',
                data: dataPie,
                backgroundColor: ['#10b981', '#d1d5db', '#ef4444'],
                hoverOffset: 4
            }]
        };

        // ✅ Render Chart
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(ctx, {
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
