@extends('base')

@section('head')
@parent
<link rel="stylesheet" href="/css/login.css" />
@stop

@section('content')

@if ($message)
<p> {{{ $message }}} </p>
@endif

<table id="login">
    <tr>
        <td>
            <form method="post" action="/login">
                <label>
                    Password:
                    <input type="password" name="password" />
                </label>

                <input type="submit" value="Login" />
            </form>
        </td>
    </tr>
</table>
@stop
