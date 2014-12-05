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
        <div id="header">
            <span id="title" title="SocialBots II"></span>

            <ul id="nav">
                @if (Route::currentRouteName() != 'login')
                <li
                    @if (strpos(Route::currentRouteName(), 'scores') !== false)
                        class="active"
                    @endif
                >
                    {{ link_to_action('ScoresController@showTeams', 'scores') }}
                </li>
                <li
                    @if (Route::currentRouteName() == 'diagnostics')
                        class="active"
                    @endif
                >
                    {{ link_to_action('DiagnosticsController@showOverview', 'diagnostics') }}
                </li>
                @else
                <li class="active">
                    {{ link_to_action('LoginController@showLogin', 'login') }}
                </li>
                @endif
            </ul>
        </div>
        @show
    
        @yield('content')
    </body>
</html>
