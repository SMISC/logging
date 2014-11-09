server {
	listen 80;
	server_name smisc.jacobgreenleaf.com;

	location /monit {
		proxy_pass http://127.0.0.1:2812;
	}

	root /usr/local/src/smisc.jacobgreenleaf.com;
	index index.php index.html;
    rewrite_log on;

	location ~ .php$ {
		include "fastcgi_params";
		fastcgi_pass 127.0.0.1:9000;
	}

	location /sql {
		try_files $uri $uri/ sql/index.php;
	}
}
