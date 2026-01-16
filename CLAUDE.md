# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a flake-based NixOS configuration managing three hosts: `laptop`, `desktop`, and `vm`. The configuration uses a modular architecture with clear separation between system-level (`modules/core/`) and user-level (`modules/home/`) settings.

## Common Commands

All commands are run via `just` (justfile):

| Command | Description |
|---------|-------------|
| `just nixos` | Rebuild and switch to the new NixOS configuration (uses `nh os switch`) |
| `just update` | Update all flake inputs (`nix flake update`) |
| `just lint` | Lint all .nix files with statix and .sh files with shellcheck |
| `just format` | Format all .nix and .sh files with treefmt |
| `just clean` | Clean Nix store older than 1 day and optimize |
| `just all` | Run full pipeline: lint, format, rebuild |

### Secrets Management (SOPS with age)

| Command | Description |
|---------|-------------|
| `just view` | View decrypted secrets |
| `just decrypt` | Decrypt secrets to file for manual editing |
| `just encrypt` | Encrypt secrets back |
| `just add <key> <value>` | Add a new secret |
| `just rem <key>` | Remove a secret |
| `just key` | Show SOPS public key |
| `just setup-sops` | Setup SOPS age key |

## Architecture

### Flake Structure

The flake is defined in `flake.nix` with:
- **Two nixpkgs channels**: `nixos-unstable` (default) and `nixos-25.05` (stable)
- **User**: `w` (git: blockton)
- **System**: `x86_64-linux`
- **SpecialArgs passed to all modules**: `self`, `user`, `inputs`, `system`, `pkgsStable`, `userSettings`, `host`

### Directory Layout

```
hosts/              # Host-specific configurations
  laptop/           # Laptop with power management (TLP, upower, powertop)
  desktop/          # Minimal desktop config
  vm/               # VM with SSH access and GRUB bootloader

modules/
  core/             # System-level NixOS modules (imported by all hosts)
    user.nix        # Home-manager integration (IMPORTANT: conditional import per host)
    system.nix      # Nix settings, cachix, timezone, locale
    nixpkgs.nix     # Package settings (allowUnfree = true)
    wayland.nix     # Hyprland + portal configuration
    xserver.nix     # X11 with auto-login
    sops.nix        # SOPS secret management
    # ... other core modules

  home/             # Home-manager modules (user-level configuration)
    default.nix     # Desktop: imports full Hyprland setup
    (directory)     # Laptop/VM: imports all modules as a directory
    hyprland/       # Hyprland WM config, hyprlock, waybar, swayosd
    programs/       # VSCodium, browsers, terminal, rofi, superfile
    terminal/       # Shell and CLI tools
    packages/       # User package sets
    languages/      # Development environments (python, nodejs, etc.)
```

### Key Architecture Pattern: Conditional Home Config

In `modules/core/user.nix:27-28`, the home-manager imports differ by host:
- **Desktop**: Imports `./../home/default.nix` (specialized Hyprland setup)
- **Laptop/VM**: Imports `./../home` as directory (modular setup)

### Build Tool: nh (Nix Helper)

The configuration uses `nh` instead of plain `nixos-rebuild`:
- `nh os switch .` - Build and switch
- `nh clean all --keep 1` - Clean old generations

### Code Formatting

treefmt is configured in `treefmt.toml`:
- **Nix files**: `nixfmt` with 80-character line width
- **Shell scripts**: `shfmt` with 4-space indentation
- Excludes: `*/packages/*`, `*/home/default.nix`, media files

## Important Inputs

The flake uses several external inputs for packages:
- `nur` - Nix User Repository
- `nix-gaming` - Gaming-related packages
- `viccinae` - Custom packages
- `bongocat` - Wayland keyboard visualizer
- `superfile` - Terminal file manager
- `zen-browser` - Zen Browser flake
- `nix-flatpak` - Flatpak integration
- `maple-mono` - Maple font (flake = false)

## Secrets

Secrets are stored in `secrets/secrets.yaml` encrypted with SOPS + age. The age key is at `~/.config/sops/age/keys.txt`. Use `just` commands for secrets management - never edit secrets.yaml directly.
