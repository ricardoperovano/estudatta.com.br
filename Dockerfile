# Site público Estudatta: HTML/CSS/JS estático servido por Nginx.
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html 404.html robots.txt sitemap.xml /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets
COPY idiomas /usr/share/nginx/html/idiomas
COPY vestibular-enem /usr/share/nginx/html/vestibular-enem
COPY ingles /usr/share/nginx/html/ingles
COPY en /usr/share/nginx/html/en
COPY concursos /usr/share/nginx/html/concursos
COPY planos /usr/share/nginx/html/planos
COPY faq /usr/share/nginx/html/faq
COPY guias /usr/share/nginx/html/guias
COPY contato /usr/share/nginx/html/contato
COPY privacidade /usr/share/nginx/html/privacidade
COPY termos /usr/share/nginx/html/termos
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
