#!/usr/bin/env python3
"""iOS simulators for one test session: create with a prefix, cap the count, delete everything after.

Usage:
  python sim_session.py plan --roles admin,user [--ram-gb 16]        # what to boot (dry run)
  python sim_session.py create <role> [--device "iPhone 17"] [--runtime "iOS 26.0"] [--no-boot]
  python sim_session.py list
  python sim_session.py cleanup [--artifacts runs/]                    # shutdown+delete ceo-* devices, remove artifacts

Every device the session creates is named `<prefix><role>` (default prefix `ceo-`), so cleanup
only ever touches devices with that prefix: the developer's own simulators survive. Cleanup also
empties the artifacts folder except `patches/` and `keep/` (what the report needs). The cap
(`--max`, default 2) exists because each booted simulator costs roughly 3-4 GB of RAM; on a 16 GB
machine the plan is one simulator plus `phx_actor.mjs` for the second role, never two simulators
by default. Set CEO_XCRUN to point at a fake xcrun in tests.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

XCRUN = os.environ.get("CEO_XCRUN", "xcrun")
PREFIX = "ceo-"
KEEP_DIRS = {"patches", "keep"}  # runs/patches (diffs) and runs/keep (clips cited in the report) are never deleted
RAM_PER_SIM_GB = 4


class TooManySimulators(RuntimeError):
    pass


def simctl(*args: str, capture: bool = True) -> str:
    result = subprocess.run([XCRUN, "simctl", *args], capture_output=capture, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"xcrun simctl {' '.join(args)} failed: {(result.stderr or '').strip()}")
    return (result.stdout or "").strip()


def catalog() -> dict:
    return json.loads(simctl("list", "-j"))


def list_devices() -> list[dict]:
    devices = []
    for runtime, entries in catalog().get("devices", {}).items():
        for entry in entries:
            devices.append({"udid": entry["udid"], "name": entry["name"], "state": entry.get("state", "?"),
                            "runtime": runtime.rsplit(".", 1)[-1], "available": entry.get("isAvailable", True)})
    return devices


def resolve(kind: str, wanted: str) -> str:
    """Identifier of a device type or runtime by (partial) name or identifier."""
    for entry in catalog().get(kind, []):
        if wanted in (entry.get("identifier"), entry.get("name")) or wanted in entry.get("name", ""):
            return entry["identifier"]
    raise RuntimeError(f"{kind}: '{wanted}' não encontrado; veja `xcrun simctl list {kind}`")


class Session:
    def __init__(self, prefix: str = PREFIX, artifacts: str = "runs", max_devices: int = 2):
        self.prefix = prefix
        self.artifacts = artifacts
        self.max_devices = max_devices

    def mine(self) -> list[dict]:
        return [d for d in list_devices() if d["name"].startswith(self.prefix)]

    def create(self, role: str, device_type: str = "iPhone 17", runtime: str = "iOS 26", boot: bool = True) -> str:
        if len(self.mine()) >= self.max_devices:
            raise TooManySimulators(f"já existem {self.max_devices} simuladores {self.prefix}*; use phx_actor.mjs para o outro papel ou suba --max")
        udid = simctl("create", f"{self.prefix}{role}", resolve("devicetypes", device_type), resolve("runtimes", runtime))
        if boot:
            simctl("boot", udid)
        os.makedirs(self.artifacts, exist_ok=True)
        return udid

    def cleanup(self) -> dict:
        removed = {"devices": [], "artifacts": []}
        for device in self.mine():
            if device["state"] == "Booted":
                simctl("shutdown", device["udid"])
            simctl("delete", device["udid"])
            removed["devices"].append(device["udid"])
        if os.path.isdir(self.artifacts):
            for name in sorted(os.listdir(self.artifacts)):
                if name in KEEP_DIRS:
                    continue  # patches and the clips the report cites survive the cleanup
                path = os.path.join(self.artifacts, name)
                removed["artifacts"].append(path)
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        return removed


def plan(roles: list[str], ram_gb: int, max_devices: int) -> str:
    budget = max(1, min(max_devices, (ram_gb - 8) // RAM_PER_SIM_GB))  # leave ~8 GB for Xcode, Metro and the server
    sims = roles[:budget]
    actors = roles[budget:]
    lines = [f"RAM {ram_gb} GB: {len(sims)} simulador(es) ({', '.join(sims)})" + (f", {len(actors)} papel(is) via phx_actor.mjs ({', '.join(actors)})" if actors else "")]
    for role in sims:
        lines.append(f"  python scripts/sim_session.py create {role}    # {PREFIX}{role}")
    for role in actors:
        lines.append(f"  node scripts/phx_actor.mjs --role {role} --url $WS_URL --topic <topic> --script <steps.json>")
    lines.append("  ... testes ...")
    lines.append("  python scripts/sim_session.py cleanup     # sempre, mesmo com falha")
    if not actors and len(roles) > 1:
        lines.append("Dois simuladores juntos: feche o Xcode e o navegador antes; se o Mac começar a paginar, volte para 1 simulador + phx_actor.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--roles", required=True)
    p.add_argument("--ram-gb", type=int, default=16)
    p.add_argument("--max", type=int, default=2)
    c = sub.add_parser("create")
    c.add_argument("role")
    c.add_argument("--device", default="iPhone 17")
    c.add_argument("--runtime", default="iOS 26")
    c.add_argument("--no-boot", action="store_true")
    c.add_argument("--max", type=int, default=2)
    c.add_argument("--artifacts", default="runs")
    sub.add_parser("list")
    k = sub.add_parser("cleanup")
    k.add_argument("--artifacts", default="runs")
    args = parser.parse_args(argv)
    if args.cmd == "plan":
        print(plan([r.strip() for r in args.roles.split(",") if r.strip()], args.ram_gb, args.max))
    elif args.cmd == "create":
        print(Session(artifacts=args.artifacts, max_devices=args.max).create(args.role, args.device, args.runtime, boot=not args.no_boot))
    elif args.cmd == "list":
        for d in list_devices():
            print(f"{d['udid']}  {d['name']}  {d['state']}  {d['runtime']}")
    elif args.cmd == "cleanup":
        removed = Session(artifacts=args.artifacts).cleanup()
        print(f"{len(removed['devices'])} simulador(es) apagado(s), {len(removed['artifacts'])} artefato(s) removido(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
