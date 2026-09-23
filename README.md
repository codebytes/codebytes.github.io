# CodeBytes blog

Source for [chris-ayers.com](https://chris-ayers.com/), built with [Hugo](https://gohugo.io/) and the [Blowfish theme](https://blowfish.page/).

## Prerequisites

- Git, including submodule support.
- [Hugo Extended](https://gohugo.io/installation/), using the version pinned by `HUGO_VERSION` in the [deployment workflow](.github/workflows/hugo.yml). The [devcontainer](.devcontainer/devcontainer.json) uses the same version.

Check your installation:

```sh
hugo version
```

The output should include `+extended`. Before upgrading Hugo, check the theme's supported version range in `themes\blowfish\config.toml`. Keep the workflow and devcontainer versions in sync.

## Get the source and theme

For a new checkout:

```sh
git clone --recurse-submodules https://github.com/codebytes/codebytes.github.io.git
cd codebytes.github.io
```

If you already have the repository, initialize the theme from the repository root:

```sh
git submodule update --init --recursive
```

The theme is a Git submodule. This command checks out the version recorded by the site, rather than upgrading to the latest theme commit.

## Run Hugo locally

From the repository root, start the development server with draft and future-dated posts included:

```sh
hugo server --buildDrafts --buildFuture
```

Open [http://localhost:1313/](http://localhost:1313/). Hugo watches for changes and reloads the browser when you save. Press `Ctrl+C` in the terminal to stop it.

Posts marked `draft: true` require `--buildDrafts` to appear in the preview. To use the site's normal content settings instead, omit the preview flags:

```sh
hugo server
```

You can also run **Terminal > Run Task > Hugo: Serve** in VS Code; that task includes both preview flags.

The theme includes its built CSS and JavaScript, so `npm install` is not required to serve or build the site.

## Build the production site

```sh
hugo --gc --minify --environment production
```

Hugo writes the generated site to the `public` directory. Draft posts remain excluded. Generated output and caches are ignored by Git and should not be committed.

## Use the devcontainer

With Docker and the VS Code Dev Containers extension installed, run **Dev Containers: Reopen in Container**. The container provides the pinned Hugo version and forwards port 1313.

In the container terminal, initialize the submodule if needed and run the same Hugo server command shown above.

## Troubleshooting

- **Missing theme or shortcode templates:** run `git submodule update --init --recursive`.
- **Incompatible Hugo version warning:** use the workflow's pinned version and check that it falls within the theme's supported range.
- **Draft post missing:** start the server with `--buildDrafts`.
- **Port 1313 is already in use:** choose another port, such as `hugo server --buildDrafts --buildFuture --port 1314`, then open `http://localhost:1314/`.
