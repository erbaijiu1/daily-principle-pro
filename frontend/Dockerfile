# build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json vite.config.ts ./ 
COPY src ./src
RUN npm i --registry=https://registry.npmmirror.com
RUN npm run build:h5

# runtime: nginx
FROM nginx:alpine
ARG API_ORIGIN
ENV API_ORIGIN=${API_ORIGIN}
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
