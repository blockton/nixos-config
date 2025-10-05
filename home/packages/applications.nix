{ pkgs, pkgs-stable, ... }:

with pkgs;
[
  vscode
  chromium
  protonvpn-gui
  pkgs.texlivePackages.wallpaper
  pkgs-stable.termius
  telegram-desktop
]
