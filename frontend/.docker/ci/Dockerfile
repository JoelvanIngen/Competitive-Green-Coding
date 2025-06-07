# Linting and unit tests Dockerfile
FROM node:24-alpine

WORKDIR /site
RUN chown node:node /site

USER node

COPY package.json package-lock.json ./

RUN npm ci --no-audit

COPY . .
