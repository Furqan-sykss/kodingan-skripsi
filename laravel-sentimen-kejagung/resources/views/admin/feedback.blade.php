@extends('layouts.app')

@section('content')
<div class="container">
    <div class="alert alert-success">
        {{ $message }}
    </div>

    <a href="{{ $next }}" class="btn btn-primary">
        {{ $next_label }}
    </a>
</div>
@endsection
