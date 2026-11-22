# KiCad Text Anchors Overlay

A lightweight KiCad PCB Editor plugin that toggles real-time anchor crosses on the `User.Comments` layer for all visible PCB texts and footprint fields across any layer.

## Features
- **One-click toggle** from the PCB Editor top toolbar or `Tools > External Plugins > Toggle Text Anchors`.
- **Real-time tracking**: Automatically updates anchor crosses as you move, edit, or add texts.
- **Clean toggle off**: Clicking the button again stops tracking and removes all temporary crosses from `User.Comments`.

## Installation

### Option 1: Plugin and Content Manager (Recommended)
1. Download the latest release `.zip` from the [Releases](../../releases) page.
2. Open KiCad **Plugin and Content Manager** -> **Install from File...** and select the `.zip`.

### Option 2: Manual Installation
Copy the contents of `plugins/` into your KiCad 3rd-party plugins directory:
- **Linux:** `~/.local/share/kicad/10.0/3rdparty/plugins/com_nekuneko_text_anchors/`
- **Windows:** `%USERPROFILE%\Documents\KiCad\10.0\3rdparty\plugins\com_nekuneko_text_anchors\`
- **macOS:** `~/Documents/KiCad/10.0/3rdparty/plugins/com_nekuneko_text_anchors/`
