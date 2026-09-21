# Edge nginx (/api, /admin, /minio, / → front). Build context: docker/nginx.
FROM nginx:1.27-alpine

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
