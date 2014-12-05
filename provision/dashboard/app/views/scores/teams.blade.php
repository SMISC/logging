@extends('base')

@section('content')

<h1>Teams</h1>

<table id="teams">
    <thead>
        <tr>
            <th rowspan="2">Team</th>
            <th rowspan="2">Bots</th>
            <th colspan="6">Scores</th>
        </tr>
        <tr>
            <th>@-mentions</th>
            <th>@-replies</th>
            <th>Follows</th>
            <th>Link Share</th>
            <th>Interaction</th>
            <th>Total</th>
        </tr>
    </thead>

@foreach ($teams as $team)
    <tr>
        <td><a href="#">{{ $team->name }}</a></td>
        <td>{{ $bots[$team->id] }}
        <td>[...]</td>
        <td>[...]</td>
        <td>[...]</td>
        <td>[...]</td>
        <td>[...]</td>
        <td>[...]</td>
    </tr>
@endforeach

</table>

@stop
