FROM node:latest as ui

WORKDIR /app/ui

COPY package*.json .
RUN npm install -g pnpm
RUN pnpm install

ADD ./ ./

RUN pnpm ng build --configuration=production --base-href /ui/ --deploy-url /ui/

FROM nginx:alpine
COPY --from=ui /app/ui/dist/ui/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf