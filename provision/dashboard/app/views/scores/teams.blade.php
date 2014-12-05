@extends('base')

@section('content')

<h1>Leaderboard</h1>

<h2>Teams</h2>

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

    <tbody>

        @foreach ($teams as $team)
        <tr>
            <td>{{ link_to_action('ScoresController@showTeam', $team->name, array($team->id)) }}</td>
            <td>{{ $bots[$team->id] }}
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
        </tr>
        @endforeach

    </tbody>

</table>

@stop
