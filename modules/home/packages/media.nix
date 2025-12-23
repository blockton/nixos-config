{ pkgs, ... }:
{
  home.packages = with pkgs; [
    ffmpeg # Complete multimedia framework
    imv # Simple image viewer
    lowfi # Lo-fi music player
    mpv # Media player
    pamixer # PulseAudio command line mixer
    playerctl # Controller for media players
    swappy # Screenshot editing tool
  ];
}
