# Production Dockerfile, builds and runs behind nginx instance
FROM node:24-alpine AS builder

WORKDIR /site
RUN chown node:node /site

USER node

COPY package.json package-lock.json ./

RUN npm ci --no-audit

COPY . .

RUN npm run build


FROM nginx:alpine

RUN apk add --no-cache curl

RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /site/out /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
