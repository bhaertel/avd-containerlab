from __future__ import annotations

import argparse
import getpass
import json
import re
import ssl
from datetime import datetime
from pathlib import Path
from typing import Any

import pyeapi
import yaml
from nornir import InitNornir
from nornir.core.task import Result, Task


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_INVENTORY_CONFIG = REPO_ROOT / "labtask" / "clab-Labtask Topology" / "nornir-simple-inventory.yml"
DEFAULT_COMMANDS_FILE = SCRIPT_DIR / "show_commands.txt"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "outputs"
FILENAME_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")
OUTPUT_FORMAT_EXTENSIONS = {"text": ".txt", "json": ".json"}
SUPPORTED_PLATFORMS = {"eos", "ceos", "arista_eos", "arista_ceos"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect EOS show command output with pyeapi scheduled by Nornir."
    )
    parser.add_argument(
        "-c",
        "--commands-file",
        type=Path,
        default=DEFAULT_COMMANDS_FILE,
        help="Text file containing one show command per line.",
    )
    parser.add_argument(
        "-i",
        "--inventory-config",
        type=Path,
        default=DEFAULT_INVENTORY_CONFIG,
        help="YAML file describing the Nornir inventory plugin and options.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where command output files are written.",
    )
    parser.add_argument(
        "-f",
        "--output-format",
        choices=sorted(OUTPUT_FORMAT_EXTENSIONS),
        default="text",
        help="Command output format to request from eAPI and write to disk.",
    )
    return parser.parse_args()


def load_commands(commands_file: Path) -> list[str]:
    commands = [
        line.strip()
        for line in commands_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not commands:
        raise ValueError(f"No commands found in {commands_file}")
    return commands


def load_inventory_config(inventory_config: Path) -> dict[str, Any]:
    config = yaml.safe_load(inventory_config.read_text(encoding="utf-8")) or {}
    plugin = config.get("plugin")
    options = config.get("options", {})
    if plugin and isinstance(options, dict):
        resolved_options = {
            key: str((inventory_config.parent / Path(value)).resolve())
            for key, value in options.items()
        }
        return {"plugin": plugin, "options": resolved_options}

    if is_host_inventory(config):
        options = {"host_file": str(inventory_config.resolve())}

        defaults_file = inventory_config.parent / "defaults.yaml"
        if defaults_file.exists():
            options["defaults_file"] = str(defaults_file.resolve())

        groups_file = inventory_config.parent / "groups.yaml"
        if groups_file.exists():
            options["group_file"] = str(groups_file.resolve())

        return {"plugin": "SimpleInventory", "options": options}

    raise ValueError(
        f"Invalid inventory config in {inventory_config}. Expected either a Nornir inventory "
        "config with 'plugin' and 'options' or a flat host inventory file."
    )


def is_host_inventory(config: Any) -> bool:
    if not isinstance(config, dict) or not config:
        return False

    reserved_keys = {"plugin", "options"}
    if reserved_keys & set(config):
        return False

    return all(
        isinstance(host_data, dict) and "hostname" in host_data
        for host_data in config.values()
    )


def sanitize_command(command: str) -> str:
    return FILENAME_SAFE.sub("_", command.strip()).strip("._") or "command"


def build_ssl_context(verify: bool) -> ssl.SSLContext | None:
    if verify:
        return None

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def format_command_output(response: Any, output_format: str) -> str:
    if isinstance(response, list) and response:
        result = response[0].get("result", {})
        if output_format == "text" and isinstance(result, dict):
            output = result.get("output")
            if isinstance(output, str):
                return output
        if output_format == "json":
            return json.dumps(result, indent=2, sort_keys=True) + "\n"

    raise ValueError(
        f"Unexpected eAPI response format for {output_format}: {response!r}"
    )


def prompt_credentials() -> tuple[str, str]:
    username = ""
    while not username:
        username = input("EOS eAPI username: ").strip()
        if not username:
            print("Username is required.")

    password = getpass.getpass("EOS eAPI password: ")
    return username, password


def collect_host_outputs(
    task: Task,
    commands: list[str],
    output_dir: Path,
    output_format: str,
    username: str,
    password: str,
) -> Result:
    output_dir.mkdir(parents=True, exist_ok=True)
    verify = bool(task.host.data.get("verify", False))
    node = pyeapi.client.connect(
        transport=task.host.data.get("transport", "https"),
        host=task.host.hostname,
        username=username,
        password=password,
        port=task.host.port,
        timeout=int(task.host.data.get("timeout", 60)),
        context=build_ssl_context(verify),
        return_node=True,
    )

    failures: list[str] = []
    written_files = 0

    for command in commands:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename = (
            f"{timestamp}_{task.host.name}_{sanitize_command(command)}"
            f"{OUTPUT_FORMAT_EXTENSIONS[output_format]}"
        )
        output_path = output_dir / filename

        try:
            response = node.enable([command], encoding=output_format, strict=False)
            command_output = format_command_output(response, output_format)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{command}: {exc}")
            command_output = f"ERROR executing '{command}' on {task.host.name}: {exc}\n"

        output_path.write_text(command_output, encoding="utf-8")
        written_files += 1

    result_summary = f"wrote {written_files} files to {output_dir}"
    if failures:
        result_summary = f"{result_summary}; failures: {'; '.join(failures)}"

    return Result(host=task.host, result=result_summary, failed=bool(failures))


def main() -> int:
    args = parse_args()
    commands = load_commands(args.commands_file.resolve())
    inventory = load_inventory_config(args.inventory_config.resolve())
    username, password = prompt_credentials()

    nr = InitNornir(
        logging={"enabled": False},
        inventory=inventory,
    )
    if not nr.inventory.hosts:
        raise ValueError(
            "No hosts found in the Nornir inventory. Start the containerlab topology first so "
            "the generated inventory files under labtask/clab-Labtask Topology are populated."
        )

    unsupported_hosts = [
        host.name
        for host in nr.inventory.hosts.values()
        if (host.platform or "").lower() not in SUPPORTED_PLATFORMS
    ]
    if unsupported_hosts:
        print(
            "Skipping unsupported hosts: "
            + ", ".join(sorted(unsupported_hosts))
            + ". This collector only supports EOS eAPI platforms."
        )
        nr = nr.filter(filter_func=lambda host: (host.platform or "").lower() in SUPPORTED_PLATFORMS)

    if not nr.inventory.hosts:
        raise ValueError("No supported EOS hosts found in the Nornir inventory.")

    results = nr.run(
        task=collect_host_outputs,
        commands=commands,
        output_dir=args.output_dir.resolve(),
        output_format=args.output_format,
        username=username,
        password=password,
    )

    failed_hosts = [host for host, multi_result in results.items() if multi_result.failed]
    for host, multi_result in results.items():
        print(f"{host}: {multi_result[0].result}")

    return 1 if failed_hosts else 0


if __name__ == "__main__":
    raise SystemExit(main())