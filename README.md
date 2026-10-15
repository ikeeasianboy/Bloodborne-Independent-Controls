# Bloodborne Independent Controls

Separates Roll/Dodge from Sprint with independent, customizable keybinds. Dodge no longer shares its input with Sprint, preventing unintended dodges when sprinting and making dodge input feel more consistent.

## Features

- Independent Sprint and Roll/Dodge bindings.
- Customizable keyboard and controller controls.
- Configure bindings in the in-game main menu.

## Default Controls

| Action | Keyboard | Xbox Controller |
|---|---|---|
| Roll / Dodge | Space | B |
| Sprint | Right Shift | L3 |

You can change these bindings in the main menu's Keybinds section.

## Requirements

- A compatible Windows BBPort source tree.
- Python 3 and MSYS2 CLANG64 with the required build dependencies.

The patch was checked against source commit `8ecba9a`. Other source revisions may not be compatible.

## Installation

1. Back up your BBPort source folder.
2. Copy `apply_dodge_sprint_patch.py` into its root.
3. Open an MSYS2 CLANG64 terminal in that folder.
4. Run `python3 apply_dodge_sprint_patch.py`.
5. If successful, rebuild with `BB_JOBS=4 bash build.sh`.
6. Launch the rebuilt game and configure your bindings in the main menu.

## Important

This release contains a source patch, not a ready-to-run executable. It does not include Bloodborne game files.

## License

GPL-2.0. See [LICENSE](LICENSE).
