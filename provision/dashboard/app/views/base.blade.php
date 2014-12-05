<!doctype html>
<html>
    <head>
        @section('head')
            <link rel="stylesheet" href="/css/main.css" />
        @show
        <title>SocialBots II</title>
    </head>
    <body>
        @section('header')
        <p id="header">
            <span id="title" title="SocialBots II"></span>

            <ul id="nav">
                @if (Route::currentRouteName() != 'login')
                <li
                    @if (strpos(Route::currentRouteName(), 'scores') !== false)
                        class="active"
                    @endif
                >
                    <a href="/scores">scores</a>
                </li>
                <li
                    @if (Route::currentRouteName() == 'diagnostics')
                        class="active"
                    @endif
                >
                    <a href="/diagnostics">diagnostics</a>
                </li>
                @else
                <li class="active">
                    <a href="/login">login</a>
                </li>
                @endif
            </ul>
        </p>
        @show
    
        @yield('content')
    </body>
</html>
