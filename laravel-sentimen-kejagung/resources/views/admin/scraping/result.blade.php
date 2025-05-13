<x-app-layout>
    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-4">
            <h3 class=" text-white font-semibold"> <a href="{{ url('/dashboard') }}">Kembali ke Dashboard</a>
            </h3>
            <p class="text-sm text-white">
                Login sebagai: <strong>{{ Auth::user()->name }}</strong> ({{ Auth::user()->role }})
            </p>
        </div>
        <h1 class="text-2xl text-center text-white">Hasil Scraping Komentar:</h1>
        <br>

        <div class="overflow-x-auto  shadow rounded-lg">
            <table class="min-w-full table-auto border text-sm">
                <thead class="bg-gray-500">
                    <tr class="text-left">
                        <th class="px-4 py-2 border">ID</th>
                        <th class="px-4 py-2 border">Video ID</th>
                        <th class="px-4 py-2 border">Username</th>
                        <th class="px-4 py-2 border">Comment</th>
                        <th class="px-4 py-2 border">Likes</th>
                        <th class="px-4 py-2 border">Tanggal Komentar</th>
                        <th class="px-4 py-2 border">Created_at</th>
                    </tr>

                    @foreach ($komentar as $item)
                        <tr class="bg-gray-50">
                            <td class="px-4 py-2 border">{{ $item->id }}</td>
                            <td class="px-4 py-2 border">{{ $item->video_id }}</td>
                            <td class="px-4 py-2 border">{{ $item->username }}</td>
                            <td class="px-4 py-2 border">{{ $item->comment }}</td>
                            <td class="px-4 py-2 border">{{ $item->likes }}</td>
                            <td class="px-4 py-2 border">{{ $item->tanggal_komentar }}</td>
                            <td class="px-4 py-2 border">{{ $item->created_at }}</td>
                        </tr>
                    @endforeach
            </table>
        </div>
    </div>

</x-app-layout>
