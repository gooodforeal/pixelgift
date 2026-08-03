FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
# TypeScript 7 ships its compiler as an optional platform package.
# Explicit inclusion prevents npm from omitting it in cross-platform Docker builds.
RUN npm ci --include=optional

COPY tsconfig.json vite.config.ts index.html ./
COPY public ./public
COPY src ./src

RUN npm run build

FROM nginx:1.27-alpine

ENV API_UPSTREAM=http://app:8000

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
