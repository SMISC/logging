@extends('base')

@section('content')

@if ($message)
<p> {{{ $message }}} </p>
@endif

<form method="post" action="/login">
    <label>
        Username:
        <input type="text" name="username" />
    </label>

    <label>
        Password:
        <input type="password" name="password" />
    </label>

    <input type="submit" value="Login" />
</form>
@stop
