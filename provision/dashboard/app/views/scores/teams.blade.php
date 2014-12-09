@extends('base')

@section('head')
@parent
<link rel="stylesheet" href="/css/scores.css" />
@stop

@section('content')

<h1>Leaderboard</h1>

<h2>Teams</h2>

<table id="teams">
    <thead>
        <tr>
            <th rowspan="2">Team</th>
            <th rowspan="2">Bots</th>
            <th class="scores" colspan="4">Scores</th>
        </tr>
        <tr>
            <th>Follows ({{ ScoresController::FOLLOW_POINTS }} pt)</th>
            <th>@ interactions ({{ ScoresController::REPLY_POINTS}} pt)</th>
            <th>Link Retweets ({{ ScoresController::LINKSHARE_POINTS}} pt)</th>
            <th>Total</th>
        </tr>
    </thead>

    <tbody>

        @foreach ($teams as $team)
        <tr>
            <td>{{ link_to_action('ScoresController@showTeam', $team->name, array($team->id)) }}</td>
            <td>{{ count($bots[$team->id]) }}
            <td>{{ $scores[$team->id]['followers'] }}</td>
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
        </tr>
        @endforeach

    </tbody>

</table>

@stop
