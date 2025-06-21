# syntax=docker/dockerfile:1

# ##################################################################
# ##################### Stage 1:    ################################
# ##################### Base image. ################################
# ##################################################################

# Start with a base image containing NodeJS so we can build Docusaurus.
FROM node:lts AS base 
ENV FORCE_COLOR=0
RUN corepack enable
WORKDIR /opt/docusaurus

# ##################################################################
# ##################### Stage 2a:         ##########################
# ##################### Development mode. ##########################
# ##################################################################
FROM base AS dev
WORKDIR /opt/docusaurus
EXPOSE 3000
CMD [ -d "node_modules" ] && npm run start -- --host 0.0.0.0 --poll 1000 || npm install && npm run start -- --host 0.0.0.0 --poll 1000

# ##################################################################
# ##################### Stage 2b:              #####################
# ##################### Production build mode. #####################
# ##################################################################
FROM base AS prod
WORKDIR /opt/docusaurus
COPY . /opt/docusaurus/
RUN npm ci
RUN npm run build

# ##################################################################
# ##################### Stage 3a:                      #############
# ##################### Serve with `docusaurus serve`. #############
# ##################################################################
FROM prod AS serve
EXPOSE 3000
CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--no-open"]

# ##################################################################
# ##################### Stage 3b:         ##########################
# ##################### Serve with Caddy. ##########################
# ##################################################################
FROM caddy:2-alpine AS caddy
COPY --from=prod /opt/docusaurus/Caddyfile /etc/caddy/Caddyfile
COPY --from=prod /opt/docusaurus/build /var/docusaurus