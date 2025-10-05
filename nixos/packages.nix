{ pkgs, pkgs-stable, ... }:
{
  nixpkgs.config = {
    allowUnfree = true;
  };

  environment.systemPackages = with pkgs; [
    nh
    nvd
    home-manager
    nix-output-monitor
  ];
}
