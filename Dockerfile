FROM node:latest as build

WORKDIR /app/ui

COPY ui/package*.json .
RUN npm install -g pnpm
RUN pnpm install

ADD ui ./

RUN pnpm ng build --configuration=production --base-href /ui/ --deploy-url /ui/

FROM python:slim

WORKDIR /app
COPY --from=build /app/ui/dist/ui static

COPY backend/requirements.txt .

RUN pip3 install -r requirements.txt

COPY backend/main.py main.py
CMD ["fastapi", "run", "main.py", "--port", "80"]

EXPOSE 80