# ---- deps: install packages, cached independently of source changes ----
FROM node:20-alpine AS deps

WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# ---- dev: source is mounted via docker-compose volume ----
FROM deps AS dev

EXPOSE 5173
CMD ["yarn", "dev", "--host"]

# ---- builder: compile for production ----
FROM deps AS builder

# VITE_ vars are baked into the bundle at build time — pass them as build args
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

COPY . .
RUN yarn build

# ---- prod: serve built files with nginx (no Node in final image) ----
FROM nginx:alpine AS prod

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
