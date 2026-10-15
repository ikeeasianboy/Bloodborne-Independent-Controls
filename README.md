# Bloodborne Independent Controls

Separates Roll/Dodge from Sprint so they can have independent keybinds. This prevents Sprint input from triggering an unwanted dodge and lets you customize both actions to fit your playstyle.

## Features

- Independent keybinds for Roll/Dodge and Sprint.
- Customizable keyboard and controller bindings.
- Change bindings through the in-game main menu.
- Includes a prebuilt Windows runtime in the release download.

## Download

**[Download the latest release](https://github.com/ikeeasianboy/Bloodborne-Independent-Controls/releases/latest)**

## Requirements

- An existing, compatible Windows Awaken's BBPort installation.
- This mod is built for the Awakenchan's BBPort source version at commit `4f93643`.
- This is not a standalone game and does not include Bloodborne game files.

## Installation

1. Close Bloodborne and Awaken's BBPort completely.
2. Download the Windows ZIP from the [Releases page](https://github.com/ikeeasianboy/Bloodborne-Independent-Controls/releases/latest) and extract it.
3. Open your `BloodbornePC\engine` folder.
4. Before installing, open the existing `out` folder and make a copy of `bb-probe.exe` named `bb-probe.original.exe`. **This backup is for uninstalling the mod** and restoring your original executable.
5. Copy the `out` folder from the extracted mod into your `BloodbornePC\engine` folder.
6. If Windows asks whether to merge folders or replace files, choose **Replace the files in the destination**.
7. Launch Bloodborne normally through Awaken's BBPort.

That's it! The mod is installed. No compiling or additional setup is required.

**Note:** This mod is intended for compatible versions of Awaken's BBPort. If your installation doesn't contain `BloodbornePC\engine\out\bb-probe.exe`, don't replace anything until you've confirmed compatibility.

## Customizing Keybinds

Open the in-game **Main Menu → Keybinds** and change the bindings for **Roll / Dodge** and **Sprint** independently.

Default keyboard bindings:

- Roll / Dodge: `Space`
- Sprint: `Right Shift`

Default Xbox controller bindings:

- Roll / Dodge: `B`
- Sprint: `L3` (press the left stick)

### Avoiding Keybind Conflicts

Make sure your new bindings don't conflict with other actions. If two actions use the same key or controller button, both may activate when you press it.

**Example:** If you assign Sprint to `LT`, remember that `LT` is the default binding for **Firearm / Parry**. Assign Firearm / Parry to another button as well to avoid triggering both actions.

The same applies to keyboard keys and other controller buttons.

## Uninstalling

1. Close Bloodborne and BBPort.
2. Restore your backup by copying `out/bb-probe.original.exe` back to `out/bb-probe.exe`.
3. Remove `IndependentControls.bat`.

If you didn't make a backup, restore the original executable from a compatible BBPort installation or package.

## Credits

- **Mod:** ikeeasianboy
- **Base project:** [Awakenchan/bloodbornebutpc](https://github.com/Awakenchan/BloodBorneButPc)
- Thanks to the original BBPort/shadPS4 developers and contributors.

## License

Distributed under GPL-2.0 as indicated by the included `LICENSE` file. Upstream code and third-party components remain subject to their respective licenses.

## Community

Join our Discord: [discord.gg/bbpc](https://discord.gg/bbpc)
