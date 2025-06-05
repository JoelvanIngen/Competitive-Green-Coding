FROM node:24-alpine AS builder
WORKDIR /site

COPY package*.json ./

# We don't need dev dependencies
RUN npm ci --omit=dev && npm cache clean --force

COPY . .
RUN npm run build

FROM node:24-alpine
WORKDIR /site

ENV NODE_ENV=production

COPY --from=builder /site/node_modules ./node_modules
COPY --from=builder /site/package*.json ./
COPY --from=builder /site/app ./app
COPY --from=builder /site/public ./public

RUN chown -R node:node /site
USER node
ENTRYPOINT ["node", "./app/page.tsx"]