# Devcontainer eos-downloader variables

If you use this repository through the devcontainer, `eos-downloader` environment variables can be loaded directly from a local runtime file. The devcontainer is configured to read `.devcontainer/eos-downloader.env` with Docker's `--env-file` support, so `ARISTA_TOKEN` and the other `ARISTA_*` values do not need to be exported in the shell that launches VS Code.

An example runtime file is available at [.devcontainer/eos-downloader.env.example](.devcontainer/eos-downloader.env.example). Copy it to `.devcontainer/eos-downloader.env`, update the placeholder values, and then rebuild or reopen the devcontainer so the container is started with the refreshed variables.

Example:

```shell
cp .devcontainer/eos-downloader.env.example .devcontainer/eos-downloader.env
```

After the container is rebuilt, `ardl` commands inside the devcontainer will automatically see the runtime-only variables from `.devcontainer/eos-downloader.env`.

## eAPI collector

Run the collector from [eapi_collector/collect_show_commands.py](/workspaces/arista/eapi_collector/collect_show_commands.py). It uses the generated Containerlab inventory for host connectivity, prompts for EOS eAPI credentials at runtime, skips non-EOS hosts, and writes command output under [eapi_collector/outputs](/workspaces/arista/eapi_collector/outputs).

Example:

```shell
cd /workspaces/arista/eapi_collector
python3 collect_show_commands.py --output-format text
python3 collect_show_commands.py --output-format json
```

Useful options: `--inventory-config` to point to a different inventory file, `--commands-file` to change the show-command list, `--output-dir` to change where files are written, and `--output-format` to choose `text` or `json`.
