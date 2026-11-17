# ⚠️ PROVISIONAL README — WRITTEN BY A LARGE LANGUAGE MODEL (LLM)

This entire README is an LLM-written draft prepared at the sole human developer’s direct request. It is provisional and will change as the project develops.

# Minecataclysm

Minecataclysm brings **Cataclysm: Dark Days Ahead** (CDDA) into a first-person 3D voxel world. The goal is to make CDDA easier to approach through familiar movement, aiming and on-screen menus while keeping the survival simulation that makes it worth playing.

CDDA runs the world, decides every gameplay outcome and owns the saves. A patched Luanti client renders the world and sends your inputs back to CDDA. Selected Mineclonia assets supply the voxel look. The two processes communicate locally through the CWM protocol.

This is a playable development build. You can explore, scavenge, fight, manage items and containers, craft, treat injuries, read and rest. NPC conversations include trade, a mission journal and individual companion orders. The project is still working toward a complete basic survival loop. See the [implementation status](IMPLEMENTATION_STATUS.md) and [roadmap](IMPLEMENTATION_PLAN.md).

## Download and play

| Platform | Path |
| --- | --- |
| **Linux desktop, x86-64** | The current development build runs on Linux. Clone the repository and follow the [build commands below](#linux-build-from-source). The developer has playtested it on Pop!_OS. |
| **Windows 11, x64** | If you already have `Minecataclysm-Windows11-Setup.exe`, double-click it and use the Minecataclysm shortcut. The October 21 installer is an older snapshot (CWM 2.26). Its automated verification used Wine. Real Windows 11 playtests are pending. The [Windows build guide](tools/windows/README.md) describes how to cross-build the installer on Linux. |
| **macOS and other platforms** | The integrated game has no verified build or installation procedure on these platforms. |

This repository distributes **source code**. [GitHub Releases](https://github.com/dannhill/minecataclysm/releases) currently has no installer or prebuilt game download. The Windows installer mentioned above was generated locally. For an installer you already have, Windows stores your saves and settings under `%LOCALAPPDATA%\Minecataclysm`. [Windows build and test details](docs/releases/windows11-2026-10-21.md)

### Linux build from source

You need Git, Bash, Python 3.10+, CMake 3.20+, a C++20 compiler, and an X11 or XWayland desktop session with working OpenGL. On Debian or Ubuntu based distributions, install the development packages:

```sh
sudo apt install git build-essential cmake pkg-config python3 gettext \
  libncurses-dev zlib1g-dev libzstd-dev libsqlite3-dev libpng-dev libjpeg-dev \
  libfreetype6-dev libgl1-mesa-dev libx11-dev libxi-dev libxxf86vm-dev \
  libopenal-dev libogg-dev libvorbis-dev libgmp-dev libjsoncpp-dev libluajit-5.1-dev
```

Clone the integration repository and reconstruct its sources:

```sh
git clone --branch prototype/playable-core https://github.com/dannhill/minecataclysm.git
cd minecataclysm
mkdir -p artifacts
git clone --depth 1 --branch v24.3.25 https://github.com/google/flatbuffers.git artifacts/flatbuffers
flatbuffers_include="$PWD/artifacts/flatbuffers/include"
python3 tools/takeover_baseline.py reconstruct --destination artifacts/local-build/workspace
cd artifacts/local-build/workspace
```

The reconstruction downloads the recorded CDDA, Luanti and Mineclonia commits, applies the integration patches and verifies the file inventories. Allow time and disk space for the upstream downloads and builds. Use a fresh destination directory for each reconstruction.

Build the two executables and their translation catalogs, then launch the game from that workspace:

```sh
cmake -S cdda -B cdda/build -DCMAKE_BUILD_TYPE=Release \
  -DCURSES=ON -DTILES=OFF -DSOUND=OFF -DTESTS=OFF -DBUILD_TESTING=OFF \
  -DLOCALIZE=ON -DLANGUAGES=it_IT \
  -DCWM_FLATBUFFERS_INCLUDE_DIR="$flatbuffers_include"
cmake --build cdda/build --target cdda-server locale --parallel 2

cmake -S luanti -B luanti/build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CLIENT=ON -DBUILD_SERVER=OFF -DRUN_IN_PLACE=ON \
  -DENABLE_LTO=OFF -DENABLE_SOUND=ON -DENABLE_GETTEXT=ON -DUSE_SDL2=OFF \
  -DCWM_FLATBUFFERS_INCLUDE_DIR="$flatbuffers_include"
cmake --build luanti/build --target luanti translations --parallel 2

./start.sh
```

`start.sh` launches `cdda/build/src/cdda-server` and `luanti/bin/luanti`. On first launch it creates the game world. CDDA saves under `user/cdda/`, the Luanti presentation cache lives under `worlds/cdda-presentation/`, and each run writes logs under `artifacts/runtime/`. Keep the CDDA save directory if you rebuild in a new workspace.

**Keep the upstream versions pinned.** The [manifest](baseline/manifest.json) records the exact source commits for all three projects. Build CDDA and Luanti from the same integration snapshot so both use the same CWM version. The game runs with the included `game/` directory and its selected assets. A separate installed copy of Mineclonia is unnecessary. This build uses the FlatBuffers 24.3.25 headers checked out above. If you regenerate the protocol or run its CMake suite, use the matching `flatc` compiler.

## First session

- **WASD** moves and the mouse looks around. **I** opens inventory, **H** the body and survival panel, and **K** crafting.
- **Right-click** interacts with nearby objects, doors, windows and NPCs. With a firearm in hand, point at a hostile, hold **right-click** to aim and click **left** to fire.
- **B** opens rest and **J** opens the journal. **F7** pauses. **F8** cycles the current time speed, with faster options during long rest.
- **Esc → Language** switches between English and the work-in-progress Italian translation during play.

## Playtesting and development

**Every manual `PASS` was reported by the project’s sole human developer after playing the game.** The developer also plays outside the checklists to judge whether the game is fun, whether it feels fluid, and where the mechanics or interface need work. They direct the project and are not a UI/UX designer. LLMs are used extensively for code and documentation. The human playtest results and the automated engineering checks have separate records.

[Human playtest results by feature](docs/validation/human-playtests.md) · [Detailed test ledger and comments](docs/validation/pending-manual.md) · [Authorship and testing statement](HUMAN_TESTING.md)

The repository also contains [architecture notes](ARCHITECTURE.md) and [asset provenance](assets-manifest.json). CDDA, Luanti and Mineclonia retain their upstream licenses. Individual media notices are included alongside the [item](game/mods/cdda_items/media-notices), [entity](game/mods/cdda_entities/media-notices) and [world](game/mods/cdda_nodes/media-notices) assets. The [CWM protocol license](protocol/LICENSE) is included separately.
