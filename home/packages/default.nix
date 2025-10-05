{ pkgs, pkgs-stable, ... }:

let
  chunks = [
    ./cli.nix
    ./cool.nix
    ./fonts.nix
    ./gnome.nix
    ./utilities.nix
    ./multimedia.nix
    ./networking.nix
    ./development.nix
    ./applications.nix
  ];
in

# Import each chunk with both pkgs & pkgs-stable, then flatten into one big list
builtins.concatLists (map (f: import f { inherit pkgs pkgs-stable; }) chunks)
