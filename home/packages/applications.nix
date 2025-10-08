{ pkgs, pkgs-stable, ... }:

(with pkgs; [
  vscode
  chromium
  protonvpn-gui
  telegram-desktop
  texlivePackages.wallpaper
])

++ (with pkgs-stable; [
  termius
  tor-browser
])