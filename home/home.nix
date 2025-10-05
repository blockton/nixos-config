{ pkgs, pkgs-stable, ... }:

{
  imports = [
    ./programs
    ./modules
  ];

  home = {
    username = "w";
    homeDirectory = "/home/w";
    stateVersion = "25.05";
  };

  nixpkgs.config.allowUnfree = true;

  home.packages =
    let
      extraPkgs = import ./packages { inherit pkgs pkgs-stable; };
    in
    (with pkgs; [
      nixd
      nixfmt-rfc-style
    ])
    ++ extraPkgs;
}
