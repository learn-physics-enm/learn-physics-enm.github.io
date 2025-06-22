# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Using Docker

1. Pull the docker image using `docker pull kinetekenergy/learn-physics-enm:latest`. You can view it [here](https://hub.docker.com/repository/docker/kinetekenergy/learn-physics-enm/general) on DockerHub.
2. Run `docker compose up --build` to start the site.
   1. Run `docker compose down` to stop the site.
3. Go to `http://localhost:3000/` in your browser to see the site.
4. Changes made to docs should update instantly

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

### Design

Our color scheme comes from [Google's Material 3](https://m3.material.io/styles/color/static/baseline).
