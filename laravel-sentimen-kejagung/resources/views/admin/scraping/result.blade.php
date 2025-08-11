<x-app-layout>
    <style>
        .result-container {
            background: white;
            border-radius: 0.75rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }

        .result-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            padding: 1.5rem;
            color: white;
        }

        .result-stats {
            background: #f8fafc;
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .stat-card {
            background: white;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .stat-icon {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #e0e7ff;
            color: #4f46e5;
        }

        .stat-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b;
        }

        .stat-label {
            font-size: 0.875rem;
            color: #64748b;
        }

        /* Table Styles Matching Dashboard */
        .table-container {
            overflow-x: auto;
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .comment-table {
            min-width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }

        .comment-table th {
            background-color: #f9fafb;
            color: #374151;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        .comment-table td {
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid #e5e7eb;
            color: #4b5563;
        }

        .comment-table tr:hover td {
            background-color: #f9fafb;
        }

        .comment-text {
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .comment-text:hover {
            white-space: normal;
            overflow: visible;
            position: absolute;
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 0.5rem;
            border-radius: 0.375rem;
            z-index: 10;
            max-width: 400px;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: white;
            transition: opacity 0.2s;
        }

        .back-link:hover {
            opacity: 0.8;
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
    </style>

    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">
        <div class="result-container">
            <!-- Header Section -->
            <div class="result-header">
                <div class="flex items-center justify-between">
                    <a href="{{ url('/') }}" class="back-link">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                                clip-rule="evenodd" />
                        </svg>
                        Kembali ke Dashboard
                    </a>
                    <p class="text-sm">
                        Login sebagai: <strong>{{ Auth::user()->name }}</strong> ({{ Auth::user()->role }})
                    </p>
                </div>
                <h1 class="text-2xl text-center mt-4 font-bold">Hasil Scraping Komentar</h1>
            </div>

            <!-- Stats Section -->
            <div class="result-stats">
                <div class="stat-card">
                    <div class="stat-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path
                                d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v1h8v-1zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-1a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v1h-3zM4.75 12.094A5.973 5.973 0 004 15v1H1v-1a3 3 0 013.75-2.906z" />
                        </svg>
                    </div>
                    <div>
                        <div class="stat-value">{{ $komentar->total() }}</div>
                        <div class="stat-label">Total Komentar</div>
                    </div>
                </div>



                <div class="stat-card">
                    <div class="stat-icon" style="background-color: #e0f2fe; color: #0ea5e9;">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                                clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div>
                        <div class="stat-value">
                            {{ \Carbon\Carbon::parse($komentar->max('created_at'))->format('d M Y') }}</div>
                        <div class="stat-label">Terakhir Diupdate</div>
                    </div>
                </div>
            </div>

            <!-- Table Section -->
            <div class="p-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-800">Data Komentar</h2>
                <p class="text-sm text-gray-600">Hasil scraping terbaru ditampilkan pertama</p>
            </div>

            <div class="table-container">
                <table class="comment-table">
                    <thead>
                        <tr>
                            <th class="px-6 py-3">No</th>
                            <th class="px-6 py-3">Username</th>
                            <th class="px-6 py-3">Komentar</th>
                            <th class="px-6 py-3">Likes</th>
                            <th class="px-6 py-3">Tanggal Komentar</th>
                            <th class="px-6 py-3">Waktu Scraping</th>
                            @if (Auth::user()->role === 'admin')
                                <th class="px-6 py-3">Aksi</th>
                            @endif
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($komentar as $item)
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ ($komentar->currentPage() - 1) * $komentar->perPage() + $loop->iteration }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                                    {{ $item->username }}
                                </td>
                                <td class="px-6 py-4">
                                    <div class="comment-text" title="{{ $item->comment }}">
                                        {{ $item->comment }}
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ $item->likes }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ $item->tanggal_komentar }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    {{ \Carbon\Carbon::parse($item->created_at)->format('d M Y H:i') }}
                                </td>
                                @if (Auth::user()->role === 'admin')
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <button type="button"
                                            class="btn-delete-mentah bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-4 rounded transition"
                                            data-id="{{ $item->id }}">
                                            Hapus
                                        </button>
                                    </td>
                                @endif
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

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script>
        // Make comment text fully visible on click
        document.querySelectorAll('.comment-text').forEach(el => {
            el.addEventListener('click', function() {
                this.classList.toggle('expanded');
            });
        });

        $.ajaxSetup({
            headers: {
                'X-CSRF-TOKEN': '{{ csrf_token() }}'
            }
        });

        $(document).on('click', '.btn-delete-mentah', function() {
            if (confirm('Yakin ingin menghapus data ini beserta hasil analisisnya?')) {
                var id = $(this).data('id');
                $.ajax({
                    url: '/admin/komentar-mentah/' + id,
                    type: 'DELETE',
                    success: function(response) {
                        if (response.success) {
                            alert('Data berhasil dihapus!');
                            location.reload();
                        } else {
                            alert('Gagal menghapus data: ' + (response.message || ''));
                        }
                    },
                    error: function() {
                        alert('Terjadi kesalahan saat menghapus data!');
                    }
                });
            }
        });
    </script>
</x-app-layout>
