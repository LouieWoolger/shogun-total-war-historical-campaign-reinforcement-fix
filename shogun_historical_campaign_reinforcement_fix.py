#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


PATCH_NAME = "Shogun: Total War Gold - Historical Campaign Reinforcement Fix"
VERSION = "v1.0.0"
EXE_NAME = "ShogunM.exe"
BACKUP_SUFFIX = ".historical-campaign-reinforcement-fix.bak"


@dataclass(frozen=True)
class BytePatch:
    name: str
    offset: int
    va: int
    original: bytes
    patched: bytes
    description: str


@dataclass(frozen=True)
class InspectResult:
    exe_path: Path
    sha256: str
    state: str
    known_hash_state: str | None
    notes: tuple[str, ...]


PATCH_STUB = bytes.fromhex(
    "8B 54 24 04"
    " 8B 81 6C 80 00 00"
    " 89 02"
    " 8B 81 70 80 00 00"
    " 89 42 04"
    " 8B 41 10"
    " 3B 81 24 78 00 00"
    " 7E 06"
    " 8B 81 24 78 00 00"
    " 89 42 08"
    " 8A 81 20 78 00 00"
    " 88 42 0C"
    " 8B 81 38 78 00 00"
    " 89 42 10"
    " C2 04 00"
)

HISTORICAL_REINFORCEMENT_PATCHES = (
    BytePatch(
        name="TimedReinforcementPositionCall",
        offset=0x000AD6E3,
        va=0x004AD6E3,
        original=bytes.fromhex("E8 78 63 F7 FF"),
        patched=bytes.fromhex("E8 D8 C3 AA 00"),
        description="Redirect timed reinforcements to the ADF-coordinate stub.",
    ),
    BytePatch(
        name="AdfCoordinateStub",
        offset=0x006F8AC0,
        va=0x00F59AC0,
        original=bytes(len(PATCH_STUB)),
        patched=PATCH_STUB,
        description="Copy the saved reinforcement coordinates into the arrival position struct.",
    ),
)

KNOWN_HASHES = {
    "4445DCB123D595A9B68FD18A20B98A9F9332F9651474976636CB9EC54F3D16AF": "original",
    "11356636154934CC2FF2ED26B46FD82155C05EB52873FE6763F7FD22B1344D32": "throne_audio_fix_only",
    "660219A520F446A4E9B7DD868596D26BF2F65FD047CAB6EDC277677CBE5C8016": "historical_reinforcement_fix_only",
    "00F5024AEC950AB82AF6C74D1824C3B73B04F5672382BA4C036D8051D2FC9F63": "throne_audio_and_historical_reinforcement_fixes",
    "1154B5703769809D56B80DDB5B25BD98DEE2DED19721AEEFA9254D3EB81A9F78": "unit_throne_harvest_fixes",
    "A1A6A1E26DB276B8CB77ECC3F951151CB9B54186EAA20AC74A04BE56B5249C7D": "unit_throne_harvest_and_historical_reinforcement_fixes",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def resolve_exe(target: str | Path) -> Path:
    path = Path(target).expanduser().resolve()
    if path.is_dir():
        path = path / EXE_NAME
    if not path.exists():
        raise FileNotFoundError(f"target not found: {path}")
    if path.name.lower() != EXE_NAME.lower():
        raise ValueError(f"target must be {EXE_NAME} or its game folder: {path}")
    return path


def backup_path(exe_path: Path) -> Path:
    return exe_path.with_name(exe_path.name + BACKUP_SUFFIX)


def inspect_exe(exe_path: Path) -> InspectResult:
    data = exe_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest().upper()
    notes: list[str] = []
    clean = 0
    patched = 0

    for patch in HISTORICAL_REINFORCEMENT_PATCHES:
        current = data[patch.offset : patch.offset + len(patch.original)]
        if current == patch.original:
            clean += 1
        elif current == patch.patched:
            patched += 1
        else:
            notes.append(
                f"{patch.name}: unsupported bytes at 0x{patch.offset:08X} "
                f"(found {current.hex(' ').upper()})"
            )

    if notes:
        state = "unknown_unsupported"
    elif clean == len(HISTORICAL_REINFORCEMENT_PATCHES):
        state = "clean_supported"
    elif patched == len(HISTORICAL_REINFORCEMENT_PATCHES):
        state = "patched"
    else:
        state = "unknown_unsupported"
        notes.append("Historical reinforcement patch is only partially present.")

    return InspectResult(
        exe_path=exe_path,
        sha256=digest,
        state=state,
        known_hash_state=KNOWN_HASHES.get(digest),
        notes=tuple(notes),
    )


def print_header() -> None:
    print(f"{PATCH_NAME} {VERSION}")
    print("=" * (len(PATCH_NAME) + len(VERSION) + 1))


def print_inspection(result: InspectResult) -> None:
    print(f"target={result.exe_path}")
    print(f"sha256={result.sha256}")
    print(f"state={result.state}")
    print(f"known_hash_state={result.known_hash_state if result.known_hash_state else 'no'}")
    backup = backup_path(result.exe_path)
    print(f"backup={backup if backup.exists() else 'not_found'}")
    for note in result.notes:
        print(f"note={note}")


def apply_patch(exe_path: Path) -> InspectResult:
    before = inspect_exe(exe_path)
    if before.state == "patched":
        print("status=already_patched")
        return before
    if before.state != "clean_supported":
        raise RuntimeError("The target executable is in an unknown or unsupported state.")

    backup = backup_path(exe_path)
    if not backup.exists():
        shutil.copy2(exe_path, backup)
        print(f"backup_created={backup}")
    else:
        print(f"backup_preserved={backup}")

    with exe_path.open("r+b") as handle:
        for patch in HISTORICAL_REINFORCEMENT_PATCHES:
            handle.seek(patch.offset)
            handle.write(patch.patched)
            print(
                f"patched {patch.name} file=0x{patch.offset:08X} "
                f"va=0x{patch.va:08X} description={patch.description}"
            )
        handle.flush()

    after = inspect_exe(exe_path)
    if after.state != "patched":
        raise RuntimeError(f"Patch was written, but verify returned state={after.state}.")
    return after


def restore_patch(exe_path: Path) -> InspectResult:
    backup = backup_path(exe_path)
    if not backup.exists():
        raise FileNotFoundError(f"backup not found: {backup}")
    shutil.copy2(backup, exe_path)
    print(f"restored_from={backup}")
    return inspect_exe(exe_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply, verify, or restore the SHOGUN: Total War Gold historical campaign reinforcement fix."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to ShogunM.exe or the game folder containing it. Defaults to the current directory.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only inspect the executable and print its detected state.",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help=f"Restore the executable from {BACKUP_SUFFIX}.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.verify and args.restore:
        parser.error("--verify and --restore cannot be used together")

    print_header()
    try:
        exe_path = resolve_exe(args.target)
        if args.verify:
            result = inspect_exe(exe_path)
        elif args.restore:
            result = restore_patch(exe_path)
        else:
            result = apply_patch(exe_path)

        print_inspection(result)
        return 0 if result.state != "unknown_unsupported" else 1
    except Exception as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
