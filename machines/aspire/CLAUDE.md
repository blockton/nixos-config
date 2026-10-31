# aspire

Acer Aspire A315-58G laptop for `w`, with an Intel Core i5-1135G7, Intel Iris Xe
and NVIDIA MX350 graphics, and a 1920×1080 built-in display.

## Hardware

- Hybrid Intel and NVIDIA graphics use the legacy NVIDIA driver.
- `wm/niri.nix` sets the built-in `eDP-1` display.

## Where its config lives

- `settings.nix` — machine options, graphics and enabled users.
- `default.nix` — hardware, shared modules and Niri imports.
- `hardware/hardware-configuration.nix` — detected disks and kernel modules.
- `wm/niri.nix` — monitor layout.
