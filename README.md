# Shogun: Total War Gold - Historical Campaign Reinforcement Fix
[![Discord](https://img.shields.io/discord/1505490825889579018?style=for-the-badge&logo=discord&label=Discord&color=5865F2)](https://discord.gg/zKbDADqWRC)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5F5F?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/louiewoolger)

Patches ShogunM.exe directly to fix broken timed reinforcements in the historical campaign mode of Shogun: Total War Gold. When a timed reinforcement is due the game reads the unit's unplaced position instead of the arrival coordinates stored in the .adf battle file; this patch corrects that. No battle data files are modified.

## Requirements

- Windows
- Python 3.9 or newer

## Usage

Pass the game folder or the path to `ShogunM.exe`:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py "F:\Games\Shogun Total War Gold"
python .\shogun_historical_campaign_reinforcement_fix.py "F:\Games\Shogun Total War Gold\ShogunM.exe"
```

With no argument, the script looks for `ShogunM.exe` in the current directory.

Inspect without writing changes:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py --verify "F:\Games\Shogun Total War Gold"
```

Restore from backup:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py --restore "F:\Games\Shogun Total War Gold"
```

`--verify` and `--restore` cannot be combined.

## Notes

Before patching, the script creates `ShogunM.exe.historical-campaign-reinforcement-fix.bak` in the same folder as the EXE. An existing backup is preserved and will not be overwritten.

Compatible with the [throne-room audio fix](https://github.com/LouieWoolger/shogun-total-war-throne-room-audio-fix), the [unit cost, training, and upkeep fix](https://github.com/LouieWoolger/shogun-total-war-unit-cost-training-upkeep-fix), and the [harvest report restoration fix](https://github.com/LouieWoolger/shogun-total-war-harvest-report-voice-fix). The patch offsets do not overlap with any of those patches and can be applied in any order.

Known SHA-256 values:

```
4445DCB123D595A9B68FD18A20B98A9F9332F9651474976636CB9EC54F3D16AF  original GOG/Steam
11356636154934CC2FF2ED26B46FD82155C05EB52873FE6763F7FD22B1344D32  throne-room audio fix only
660219A520F446A4E9B7DD868596D26BF2F65FD047CAB6EDC277677CBE5C8016  historical reinforcement fix only
00F5024AEC950AB82AF6C74D1824C3B73B04F5672382BA4C036D8051D2FC9F63  throne-room audio + historical reinforcement fixes
1154B5703769809D56B80DDB5B25BD98DEE2DED19721AEEFA9254D3EB81A9F78  unit-cost + throne-room audio + harvest report fixes
A1A6A1E26DB276B8CB77ECC3F951151CB9B54186EAA20AC74A04BE56B5249C7D  unit-cost + throne-room audio + harvest report + historical reinforcement fixes
```

Status messages from `--verify`:

- `state=clean_supported` — the EXE can be patched
- `state=patched` — this fix is already applied; no changes were made
- `state=unknown_unsupported` — unexpected bytes at one or more patch locations; restore a clean `ShogunM.exe` first
