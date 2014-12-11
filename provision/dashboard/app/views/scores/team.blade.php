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
        </tr>
    </thead>

    <tbody>
        @foreach ($bots as $bot)
        <tr>
            <td><a {{ ($bot['kill_date'] != null) ? 'class="kia" title="Killed"' : '' }} href="//twitter.com/{{{ $bot['screen_name'] }}}">@{{{ $bot['screen_name'] }}}</a></td>
            <td>{{ $scores[$bot['twitter_id']][Score::TYPE_FOLLOW] }} pt</td>
            <td>{{ $scores[$bot['twitter_id']][Score::TYPE_REPLY] }} pt</td>
        </tr>
        @endforeach
    </tbody>
</table>

@stop
