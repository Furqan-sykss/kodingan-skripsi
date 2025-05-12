<!DOCTYPE html>
<html>

<head>
    <title>Dashboard - Scraping TikTok</title>
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
</head>

<body>

    <button id="scrapeButton">Scrape Sekarang</button>
    <img id="loading" src="{{ asset('images/loading.gif') }}" alt="Loading...">

    <script>
        $('#scrapeButton').on('click', function() {
            $('#loading').show();
            $.ajax({
                url: "http://127.0.0.1:5000/scrape",
                type: "POST",
                headers: {
                    'X-CSRF-TOKEN': '{{ csrf_token() }}' // ⬅️ Tambahkan ini
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


</body>

</html>
