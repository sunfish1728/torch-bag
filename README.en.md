# Torch Bag

[繁體中文](README.md) · [简体中文](README.zh_CN.md) · [English](README.en.md)

An automatic torch-placement mod for Minecraft Forge 1.20.1 and NeoForge 1.21.1. Current version: 0.5.2.

## Installation

1. Download the JAR that matches your Minecraft version and place it in the instance `mods` folder.
2. In multiplayer, install Torch Bag on both the server and every client.
3. Curios API is optional. When present, Torch Bag adds a Belt slot automatically.
4. Sophisticated Backpacks and Sophisticated Core are optional. When present, Torch Bag can draw torches from those backpacks.

The Forge 1.20.1 and NeoForge 1.21.1 JARs are separate and must not be mixed.

## Torch Bag

- Right-click to open its storage; it accepts vanilla torches only.
- It holds 54 stacks, the same capacity as a double chest.
- Hold it in either hand or equip it in the Curios Belt slot to light dark areas automatically.
- Press `V` while equipped to open it. The key can be changed in Minecraft controls.
- The gear button sets the auto-light radius to 8, 16, 32, or 64 blocks; the default is 16.
- Torches are taken from the Torch Bag first, then the player inventory, then Sophisticated Backpacks.

Torch Bag recipe:

| Leather | Torch | Leather |
|---|---|---|
| Torch | Chest | Torch |
| Leather | Ender Pearl | Leather |

## Torch Bombs

Torch Bomb I, II, and III use chunk radii of 4, 8, and 16:

| Tier | Chunk area | Chunks |
|---|---:|---:|
| I | 9×9 | 81 |
| II | 17×17 | 289 |
| III | 33×33 | 1,089 |

Craft I with an Eye of Ender surrounded by four Blocks of Coal. Combine two I bombs for II, then two II bombs for III.

Right-click to consume a bomb and light outward in a chunk spiral starting at the release chunk. Creative mode does not consume it. A bomb only attempts to light space connected to the release position, so it does not pass directly through complete walls or into sealed rooms.

For speed, a normal chunk samples 25 representative columns and the release chunk samples at most 36. Valid positions are placed immediately. This deliberately favors speed, so very narrow or heavily winding passages can be skipped. The Boss Bar shows torch-placement progress. A player cannot use another bomb until their progress reaches 100%; overlapping player jobs share recent placements to avoid double density.

## Development and validation

- `forge-1.20.1/` uses Java 17 and Forge 47.4.10.
- `neoforge-1.21.1/` uses Java 21 and NeoForge 21.1.251.
- `scripts/generate_sources.py` and `scripts/generate_resources.py` generate shared content for both targets.
- Each target runs ten GameTests in four dependency combinations: all optional dependencies, none, Curios only, and Sophisticated Backpacks only.

See [TESTING.md](TESTING.md) for the detailed validation record.
