FROM node:24-alpine

RUN apk add --no-cache curl

WORKDIR /site
RUN chown node:node /site

COPY --chown=node:node package*.json .
USER node
RUN npm install

COPY --chown=node:node . .

ENTRYPOINT ["npm", "run", "dev"]