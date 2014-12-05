@extends('base')

@section('content')

<h1>Current Snapshot Progress</h1>

<dl>
    @foreach ($snapshots as $snapshot)
    <dt>{{ $snapshot['name'] }}</dt>
    <dd>{{ number_format($snapshot['length']) }} of {{ number_format($snapshot['target_size']) }}</dd>
    @endforeach

    @if (count($snapshots) == 0)
    <span>Found no snapshots.</span>
    @endif
</dl>

<h1>Historical Snapshots</h1>
    @foreach ($snapshots as $snapshot)
    <dt>{{ $snapshot['name'] }}</dt>
    <dd>{{ number_format($snapshot['count']) }}</dd>
    @endforeach

    @if (count($snapshots) == 0)
    <span>Found no snapshots.</span>
    @endif
</h1>

<h1>Backups</h1>
<dl>
    @foreach ($backups as $type => $backup_count)
        <dt>{{ $type }}</dt>
        <dd>{{ $backup_count }}</dd>
    @endforeach
    @if (count($backups) == 0)
    <span>Found no backups.</span>
    @endif
<dl>

@stop
