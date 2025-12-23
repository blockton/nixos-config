{ inputs, pkgs, ... }:
{
  imports = [ inputs.nix-index-database.homeModules.nix-index ];

  programs = {
    nix-index = {
      enable = true;
      symlinkToCacheHome = true;
      enableZshIntegration = false;
    };

    nix-index-database.comma.enable = true;
  };

  home.packages = with pkgs; [
    nix-btm # Bottom-like system monitor for Nix
    nix-du # Tool to determine which gc-roots take space in your Nix store
    nix-melt # Ranger-like flake.lock viewer
    nix-output-monitor # Processes output of Nix commands with pretty information
    nix-tree # Interactively browse Nix store paths dependencies
    nix-web # Web interface for the Nix store
    nvd # Nix/NixOS package version diff tool
  ];
}
