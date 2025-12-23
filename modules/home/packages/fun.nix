{ pkgs, ... }:
{
  home.packages = with pkgs; [
    asciiquarium-transparent # Terminal aquarium screensaver
    cbonsai # Growing bonsai tree animation
    cmatrix # Matrix rain animation
    countryfetch # Display country information
    cowsay # Cows with ASCII art messages
    figlet # Create ASCII art banners
    fortune # Display random quotes
    lavat # Lava lamp animation
    lolcat # Rainbow colored text output
    pipes # Animated pipes in terminal
    sl # Steam locomotive animation
    tty-clock # Digital clock in terminal
  ];
}
