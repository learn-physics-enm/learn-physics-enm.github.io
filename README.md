# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Using Docker

The dockerfile and dockerignore files should be already set up. Go [here](https://docusaurus.community/knowledge/deployment/docker/?target=dev#building-the-docker-image) to learn how to build and run the image along with composing. 

You don't need to go through the create and expose section unless something needs to be change (once again, it should all be set up).


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
