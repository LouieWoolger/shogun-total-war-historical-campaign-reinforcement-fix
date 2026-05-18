# Shogun: Total War Gold - Historical Campaign Reinforcement Fix

Patches `ShogunM.exe` directly to fix broken timed reinforcements in several historical campaign battles.

## What it fixes

Some historical campaign battles use `Reinforcements::` entries in their `.adf` army files. The game reads those entries, but when a timed reinforcement is due to arrive it tries to use the unit's current battlefield position. That unit has not been placed yet, so the battle can fail or behave incorrectly.

This patch makes the game use the reinforcement arrival coordinates already stored from the `.adf` file. The campaign data is left intact, so the scripted reinforcement timing is preserved.

## What it does not change

- It does not edit `.adf`, `.bdf`, or `.hcf` battle files.
- It does not remove any `Reinforcements::` entries.
- It does not change the 16 active units per side limit.
- It does not touch anything outside `ShogunM.exe`.

## Requirements

- Windows
- Python 3.9 or newer

## Usage

Pass the game folder or the path to `ShogunM.exe`:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py "F:\Games\Shogun Total War Gold"
python .\shogun_historical_campaign_reinforcement_fix.py "F:\Games\Shogun Total War Gold\ShogunM.exe"
```

With no argument, the script looks for `ShogunM.exe` in the current directory:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py
```

Inspect without writing changes:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py --verify "F:\Games\Shogun Total War Gold"
```

Restore from backup:

```powershell
python .\shogun_historical_campaign_reinforcement_fix.py --restore "F:\Games\Shogun Total War Gold"
```

`--verify` and `--restore` cannot be combined.

## Prepatched EXE

`prepatched\ShogunM.exe` is built from the original GOG/Steam executable with:

- this historical campaign reinforcement fix
- the throne-room audio fix

## Backup and restore

Before patching, the script creates:

```text
ShogunM.exe.historical-campaign-reinforcement-fix.bak
```

in the same folder as the executable. An existing backup is preserved and will not be overwritten.

## Compatibility

The patcher validates the exact bytes at its own patch locations before writing. It only changes the timed-reinforcement call and a separate unused code cave.

It is compatible with:

- [shogun-total-war-throne-room-audio-fix](https://github.com/LouieWoolger/shogun-total-war-throne-room-audio-fix)
- [shogun-total-war-unit-cost-training-upkeep-fix](https://github.com/LouieWoolger/shogun-total-war-unit-cost-training-upkeep-fix)
- [shogun-total-war-harvest-report-voice-fix](https://github.com/LouieWoolger/shogun-total-war-harvest-report-voice-fix)

## Known SHA-256 values

```text
4445DCB123D595A9B68FD18A20B98A9F9332F9651474976636CB9EC54F3D16AF  original GOG/Steam
11356636154934CC2FF2ED26B46FD82155C05EB52873FE6763F7FD22B1344D32  throne-room audio fix only
660219A520F446A4E9B7DD868596D26BF2F65FD047CAB6EDC277677CBE5C8016  historical reinforcement fix only
00F5024AEC950AB82AF6C74D1824C3B73B04F5672382BA4C036D8051D2FC9F63  throne-room audio + historical reinforcement fixes
1154B5703769809D56B80DDB5B25BD98DEE2DED19721AEEFA9254D3EB81A9F78  unit-cost + throne-room audio + harvest report fixes
A1A6A1E26DB276B8CB77ECC3F951151CB9B54186EAA20AC74A04BE56B5249C7D  unit-cost + throne-room audio + harvest report + historical reinforcement fixes
```

## Notes

- `state=clean_supported` means the EXE can be patched.
- `state=patched` means this fix is already applied.
- `state=unknown_unsupported` means one of this patch's byte locations contains unexpected data.
- Close the game before patching.
