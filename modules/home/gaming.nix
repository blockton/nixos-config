{ pkgs, inputs, ... }:
{
  home.packages = with pkgs; [
    ## Utils
    # gamemode
    # gamescope
    # winetricks
    # inputs.nix-gaming.packages.${pkgs.stdenv.hostPlatform.system}.wine-ge

    ## Minecraft
    # prismlauncher

    ## Cli games
    vitetris
    nethack

    ## Celeste
    # olympus
    # celeste-classic
    # celeste-classic-pm

    ## Doom
    # gzdoom
    crispy-doom

    ## Emulation
    sameboy
    snes9x
    # cemu
    # dolphin-emu
  ];
}
