{ pkgs, pkgs-stable, ... }:

(with pkgs; [
  vscode
  chromium
  claude-code
  protonvpn-gui
  telegram-desktop
  texlivePackages.wallpaper
])

++ (with pkgs-stable; [
  termius
  tor-browser
])