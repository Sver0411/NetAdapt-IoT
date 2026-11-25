#!/usr/bin/env python3
"""Compile & benchmark pure C11 NetAdapt-IoT gateway scheduler on host and ESP32-S3 Xtensa."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
C11_DIR = ROOT / "src/netadapt/c11"
OUT_PATH = ROOT / "output/phase2_c11/benchmark.json"


def _find_esp32s3_gcc() -> str | None:
    cand = shutil.which("xtensa-esp32s3-elf-gcc") or shutil.which("xtensa-esp-elf-gcc")
    if cand:
        return cand
    pio_pkg = Path.home() / ".platformio/packages"
    for pat in ("toolchain-xtensa-esp32s3/bin/xtensa-esp32s3-elf-gcc", "toolchain-xtensa-esp-elf/bin/xtensa-esp-elf-gcc"):
        p = pio_pkg / pat
        if p.is_file():
            return str(p)
    return None


def _parse_size_out(out: str) -> dict:
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    parts = lines[-1].split()
    return dict(text_bytes=int(parts[0]), data_bytes=int(parts[1]), bss_bytes=int(parts[2]), total_bytes=int(parts[3]))


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        # 1. Host benchmark (-O2)
        bench_bin = tdir / "bench_main"
        subprocess.run(
            [
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
                str(C11_DIR / "netadapt_sched.c"), str(C11_DIR / "bench_main.c"),
                "-lm", "-o", str(bench_bin),
            ],
            check=True,
        )
        run = subprocess.run([str(bench_bin)], capture_output=True, text=True, check=True)
        lines = [json.loads(ln) for ln in run.stdout.splitlines() if ln.strip()]
        sizes = lines[0]
        timings = lines[1:]

        # Host object size
        host_obj = tdir / "netadapt_sched_host.o"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Os", "-c", str(C11_DIR / "netadapt_sched.c"), "-o", str(host_obj)],
            check=True,
        )
        host_size_raw = subprocess.run(["size", str(host_obj)], capture_output=True, text=True, check=True).stdout
        host_cc_ver = subprocess.run(["cc", "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]

        # 2. ESP32-S3 Xtensa cross-compile (-Os)
        esp_gcc = _find_esp32s3_gcc()
        esp_info = None
        if esp_gcc:
            esp_size_tool = str(Path(esp_gcc).with_name(Path(esp_gcc).name.replace("-gcc", "-size")))
            esp_obj = tdir / "netadapt_sched_esp32s3.o"
            flags = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-Os", "-mlongcalls", "-ffunction-sections", "-fdata-sections"]
            subprocess.run([esp_gcc, *flags, "-c", str(C11_DIR / "netadapt_sched.c"), "-o", str(esp_obj)], check=True)
            sz_out = subprocess.run([esp_size_tool, str(esp_obj)], capture_output=True, text=True, check=True).stdout
            esp_ver = subprocess.run([esp_gcc, "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
            esp_info = dict(
                compiler=esp_ver,
                flags=" ".join(flags),
                netadapt_sched_o=_parse_size_out(sz_out),
                note="Exact ELF section sizes compiled for Xtensa ESP32-S3 (-Os). Runtime latency is host-measured; physical ESP32-S3 cycle/current profiling remains future work.",
            )

        payload = dict(
            host_platform=platform.platform(),
            host_machine=platform.machine(),
            host_compiler=host_cc_ver,
            static_ram=sizes,
            host_latency_scaling=timings,
            host_size_output=host_size_raw.strip(),
            esp32s3_cross_compile=esp_info,
        )
        OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
