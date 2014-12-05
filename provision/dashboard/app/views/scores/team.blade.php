@extends('base')

@section('content')

<h1>Team {{{ $team->name }}}</h1>

<h2>Bots</h2>

<table>
    <thead>
        <tr>
            <th>Handle</th>
        </tr>
    </thead>

    <tbody>
        @foreach ($bots as $bot)
        <tr>
            <td>@{{{ $bot->screen_name }}}</td>
        </tr>
        @endforeach
    </tbody>
</table>

@stop
