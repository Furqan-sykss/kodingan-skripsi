<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>{{ config('app.name', 'Laravel') }}</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.bunny.net">
    <link href="https://fonts.bunny.net/css?family=figtree:400,500,600&display=swap" rel="stylesheet" />

    <!-- Scripts -->
    @vite(['resources/css/app.css', 'resources/js/app.js'])

    <style>
        :root {
            --primary-color: #4f46e5;
            --secondary-color: #7c3aed;
            --dark-bg: #1a1a2e;
            --content-bg: #f8fafc;
        }

        body {
            background-color: var(--dark-bg);
        }

        .min-h-screen {
            background: linear-gradient(135deg, var(--dark-bg) 0%, #16213e 100%);
        }
    </style>
</head>

<body class="font-sans antialiased">
    <div class="min-h-screen">
        @include('layouts.navigation')

        <!-- Page Content -->
        <main class="pb-10">
            {{ $slot }}
        </main>
    </div>
</body>

</html>
