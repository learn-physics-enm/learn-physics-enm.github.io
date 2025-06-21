# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Using Docker

Pull the docker image using `docker pull kinetekenergy/learn-physics-enm`.

The dockerfile and dockerignore files should be already set up. Go [here](https://docusaurus.community/knowledge/deployment/docker/?target=dev#building-the-docker-image) to learn how to build and run the image along with composing.

You don't need to go through the create and expose section unless something needs to be change (once again, it should all be set up).

The version you pulled will be `dev`, not `serve` or `caddy` becuase the front-end doesn't need Docker for deployment. It's only used for development purposes.

### Gimme the commands

- `docker pull kinetekenergy/learn-physics-enm`
- `docker build --target dev -t kinetekenergy/learn-physics-enm .`
- `docker run --rm -d -p 3000:3000 -v $(pwd):/opt/docusaurus kinetekenergy/learn-physics-enm`
  - If you're using PowerShell: `docker run --rm -d -p 3000:3000 -v ${pwd}:/opt/docusaurus kinetekenergy/learn-physics-enm`

Using compose:

- `docker compose --file ./dev.docker-compose.yml up -d --build`

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
