@extends('base')

@section('head')
@parent
<link rel="stylesheet" href="/css/scores.css" />
@stop

@section('content')

<h1>Team {{{ $team->name }}}</h1>

<h2>Bots</h2>

<table>
    <thead>
        <tr>
            <th>Handle</th>
            <th>Follows ({{ ScoresController::FOLLOW_POINTS }} pt)</th>
            <th>@ interactions ({{ ScoresController::REPLY_POINTS}} pt)</th>
            <th>Link Retweets ({{ ScoresController::LINKSHARE_POINTS}} pt)</th>
            <th>Total</th>
        </tr>
    </thead>

    <tbody>
        @foreach ($bots as $bot)
        <tr>
            <td><a href="//twitter.com/{{{ $bot['screen_name'] }}}">@{{{ $bot['screen_name'] }}}</a></td>
            <td>{{ $scores[$bot['twitter_id']]['followers'] }}</td>
            <td>[...]</td>
            <td>[...]</td>
            <td>[...]</td>
        </tr>
        @endforeach
    </tbody>
</table>

@stop
