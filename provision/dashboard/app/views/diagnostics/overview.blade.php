@extends('base')

@section('content')

<h1>Snapshots</h1>

<dl>
@foreach ($snapshots as $snapshot)
    <dt>{{ $snapshot['name'] }}</dt>
    <dd>{{ $snapshot['length'] }} of {{ $snapshot['target_size'] }}</dd>
@endforeach
</dl>

<h1>Backups</h1>
@foreach ($backups as $type => $backup_count)
    <dt>{{ $type }}</dt>
    <dd>{{ $backup_count }}</dd>
@endforeach
<dl>

@stop
