<!doctype html>
<html>
    <head>
        @section('head')
            <link rel="stylesheet" href="/css/main.css" />
        @show
    </head>
    <body>
        @section('header')
            <h1 id="title">
                SocialBots II
            </h1>

            <ul id="nav">
                @if ($logged_in)
                <li
                    @if ($page == 'scores')
                        class="active"
                    @endif
                >
                    <a href="/scores">scores</a>
                </li>
                <li
                    @if ($page == 'diagnostics')
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
        @show
    
        @yield('content')
    </body>
</html>
