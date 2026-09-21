# SPA build + static nginx. Build context: repo root.
FROM node:22-alpine AS build

WORKDIR /app

COPY front/package.json front/package-lock.json ./

RUN npm ci --include=optional

COPY front/tsconfig.json front/vite.config.ts front/index.html ./
COPY front/public ./public
COPY front/src ./src

RUN npm run build

FROM nginx:1.27-alpine

COPY docker/front/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
