<x-app-layout>
    <div class="py-6 max-w-7xl mx-auto sm:px-6 lg:px-8">
        <h1 class="text-2xl font-bold mb-4">Pelabelan Manual VADER</h1>

        @if (session('success'))
            <div class="bg-green-500 text-white p-3 mb-4">
                {{ session('success') }}
            </div>
        @endif

        <form action="{{ route('vader.labeling.update') }}" method="POST">
            @csrf
            <table class="min-w-full bg-white">
                <thead>
                    <tr>
                        <th class="px-4 py-2 border">ID</th>
                        <th class="px-4 py-2 border">Komentar</th>
                        <th class="px-4 py-2 border">Label VADER</th>
                        <th class="px-4 py-2 border">Label Manual</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($komentar as $item)
                        <tr>
                            <td class="border px-4 py-2">{{ $item->id }}</td>
                            <td class="border px-4 py-2">{{ $item->comment }}</td>
                            <td class="border px-4 py-2 text-center">{{ $item->label_vader }}</td>
                            <td class="border px-4 py-2 text-center">
                                <select name="label[{{ $item->id }}]" class="border rounded">
                                    <option value="positif" {{ $item->label_vader == 'positif' ? 'selected' : '' }}>Positif</option>
                                    <option value="netral" {{ $item->label_vader == 'netral' ? 'selected' : '' }}>Netral</option>
                                    <option value="negatif" {{ $item->label_vader == 'negatif' ? 'selected' : '' }}>Negatif</option>
                                </select>
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>

            <div class="mt-4">
                <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">
                    ✅ Simpan Pelabelan
                </button>
            </div>
        </form>
    </div>
</x-app-layout>
