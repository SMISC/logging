server {
    listen 80;
    server_name smisc.jacobgreenleaf.com;
    location / {
        return 301 https://smisc.jacobgreenleaf.com$request_uri;
    }
}

server {
    listen              443 ssl;
    ssl_certificate     /usr/local/share/nginx/smisc.jacobgreenleaf.com.crt;
    ssl_certificate_key /usr/local/share/nginx/smisc.jacobgreenleaf.com.key;

    root                /usr/local/src/smisc.jacobgreenleaf.com/empty;
    index               index.html index.php;

    location /monit {
        proxy_pass      http://127.0.0.1:2812/;
    }

    location ~ \.php$ {
        include         "fastcgi_params";
        fastcgi_pass    127.0.0.1:9000;
    }

    location /sql {
        root            /usr/local/src/smisc.jacobgreenleaf.com/sql;
        try_files       $uri $uri/ sql/index.php;
    }

    location /dashboard {
        root            /usr/local/src/smisc.jacobgreenleaf.com/dashboard/laravel/public;
    }

    location = / {
        return          301 "https://smisc.jacobgreenleaf.com/dashboard/";
    }
}
