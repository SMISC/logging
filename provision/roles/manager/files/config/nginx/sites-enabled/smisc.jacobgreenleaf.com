server {
    listen              80;
    server_name         smisc.jacobgreenleaf.com;
    location / {
        return              301 https://smisc.jacobgreenleaf.com$request_uri;
    }
}

server {
    listen              80;
    server_name         smisc-sql.jacobgreenleaf.com;

    index               index.html index.php;
    root                /usr/local/src/jacobgreenleaf.com/sql;

    location ~ \.php$ {
        include             "fastcgi_params";
        fastcgi_pass        127.0.0.1:9000;
    }
}

server {
    listen              80;
    server_name         smisc-grafana.jacobgreenleaf.com;
    root                /usr/local/src/jacobgreenleaf.com/grafana;

    location / {
        try_files $uri /index.html;
    }
}

server {
    listen              443 ssl;
    server_name         smisc.jacobgreenleaf.com;
    ssl_certificate     /usr/local/share/nginx/smisc.jacobgreenleaf.com.crt;
    ssl_certificate_key /usr/local/share/nginx/smisc.jacobgreenleaf.com.key;

    index               index.html index.php;

    root      /usr/local/src/jacobgreenleaf.com/dashboard/public;

    location ~ \.php$ {
        include             "fastcgi_params";
        fastcgi_pass        127.0.0.1:9000;
    }

    location / {
        try_files $uri /index.php?$args;
    }
}
