# Production Dockerfile, builds and runs behind nginx instance
FROM node:24-alpine AS builder

WORKDIR /site

COPY package.json package-lock.json ./

RUN npm ci --no-audit

COPY . .

RUN npm run build -- --no-lint


FROM nginx:alpine

RUN apk add --no-cache curl

RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /site/.next /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
