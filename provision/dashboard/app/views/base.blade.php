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
                dashboard
            </h1>
        @show
    
        @yield('content')
    </body>
</html>
