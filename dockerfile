# syntax=docker/dockerfile:1

# Stage 1: Base image.
## Start with a base image containing NodeJS so we can build Docusaurus.
FROM node:lts-alpine AS base
## Disable colour output from yarn to make logs easier to read.
ENV FORCE_COLOR=0
## Enable corepack.
RUN corepack enable
## Set the working directory to `/opt/docusaurus`.
WORKDIR /opt/docusaurus

# Stage 2a: Development mode.
FROM base AS dev
## Set the working directory to `/opt/docusaurus`.
WORKDIR /opt/docusaurus
## Expose the port that Docusaurus will run on.
EXPOSE 3000
## run the development server
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
CMD ["/usr/local/bin/docker-entrypoint.sh"]

# Stage 2b: Production build mode.
FROM base AS prod
## Set the working directory to `/opt/docusaurus`.
WORKDIR /opt/docusaurus
## Copy over the source code.
COPY . /opt/docusaurus/
## Install dependencies with `--immutable` to ensure reproducibility.
RUN npm ci
## Build the static site.
RUN npm run build

# Stage 3a: Serve with `docusaurus serve`.
FROM prod AS serve
## Expose the port that Docusaurus will run on.
EXPOSE 3000
## Run the production server.
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--no-open"]

# Stage 3b: Serve with Caddy.
# use the latest caddy 2 alpine image to reduce vulnerabilities
FROM caddy:2-alpine AS caddy
## Copy the Caddyfile.
COPY --from=prod /opt/docusaurus/Caddyfile /etc/caddy/Caddyfile
## Copy the Docusaurus build output.
COPY --from=prod /opt/docusaurus/build /var/docusaurus

## Expose the port that Caddy will run on.

CMD ["npm", "start", "--", "--host", "0.0.0.0", "&&", "npm", "start", "--", "--poll", "1000"]