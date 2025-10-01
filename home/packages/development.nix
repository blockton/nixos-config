{ pkgs, pkgs-stable }:

(with pkgs-stable; [
  gcc # C/C++ compiler
  cmake # C/C++ build system
])

++ (with pkgs; [
  nil # Nix language server
  just # Justfile runner
  ngrok #ngrok tunneling tool
  nixpkgs-fmt # Nix formatting
])