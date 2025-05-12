<!DOCTYPE html>
<html>

<head>
    <title>Hasil Scraping TikTok</title>
</head>

<body>

    <h3>Hasil Scraping Komentar:</h3>

    <a href="{{ url('/dashboard') }}">Kembali ke Dashboard</a>
    <br>
    <br>

    <table border="1">
        <tr>
            <th>ID</th>
            <th>Video ID</th>
            <th>Username</th>
            <th>Comment</th>
            <th>Tanggal Komentar</th>
        </tr>

        @foreach ($komentar as $item)
            <tr>
                <td>{{ $item->id }}</td>
                <td>{{ $item->video_id }}</td>
                <td>{{ $item->username }}</td>
                <td>{{ $item->comment }}</td>
                <td>{{ $item->tanggal_komentar }}</td>
            </tr>
        @endforeach
    </table>

</body>

</html>
