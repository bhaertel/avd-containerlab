# Devcontainer eos-downloader variables

If you use this repository through the devcontainer, `eos-downloader` environment variables can be loaded directly from a local runtime file. The devcontainer is configured to read `.devcontainer/eos-downloader.env` with Docker's `--env-file` support, so `ARISTA_TOKEN` and the other `ARISTA_*` values do not need to be exported in the shell that launches VS Code.

An example runtime file is available at [.devcontainer/eos-downloader.env.example](.devcontainer/eos-downloader.env.example). Copy it to `.devcontainer/eos-downloader.env`, update the placeholder values, and then rebuild or reopen the devcontainer so the container is started with the refreshed variables.

Example:

```shell
cp .devcontainer/eos-downloader.env.example .devcontainer/eos-downloader.env
```

After the container is rebuilt, `ardl` commands inside the devcontainer will automatically see the runtime-only variables from `.devcontainer/eos-downloader.env`.
