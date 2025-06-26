# Production Dockerfile, builds and runs behind nginx instance
FROM node:24-alpine AS builder

WORKDIR /site

COPY package.json package-lock.json ./

RUN npm ci --no-audit

COPY . .

RUN npm run build -- --no-lint


FROM node:24-alpine AS runner

RUN apk add --no-cache curl

WORKDIR /site

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit

COPY --from=builder /site/.next ./.next
COPY --from=builder /site/public ./public

CMD ["npm", "start"]
