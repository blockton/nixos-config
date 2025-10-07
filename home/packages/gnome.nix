{ pkgs-stable, ... }:

(with pkgs-stable; [
  gnome-tweaks
  gnome-clocks
  dconf-editor
  gnome-calendar
  gnome-software
  gnome-text-editor
  gnome-disk-utility
])

++ (with pkgs-stable.gnomeExtensions; [
  dash-to-panel
  clipboard-history
  desktop-icons-ng-ding
])
