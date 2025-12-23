{ pkgs, ... }:
{
  home.packages = with pkgs; [
    age
    sops
    just
    aoc-cli # Advent of Code command-line tool
    asciinema # Record terminal sessions
    caligula # User-friendly, lightweight TUI for disk imaging
    file # Show file information
    gping # Ping with a graph
    gtrash # rm replacement, put deleted files in system trash
    jq # JSON processor
    killall # Kill processes by name
    libnotify # Send desktop notifications
    mimeo # Open files with their default application
    openssl # Cryptography toolkit
    pastel # CLI to manipulate colors
    poweralertd # Power alert daemon
    scooter # Interactive find and replace in the terminal
    sshpass # Non-interactive ssh password provider
    tldr # Simplified man pages
    tokei # Project line counter
    translate-shell # CLI translator
    udiskie # Automounter for removable media
    wavemon # Monitoring for wireless network devices
    wget # File downloader
    winetricks # Wine configuration tool
    woomer # Tool for screenshot management
    xdg-utils # Desktop integration utilities
  ];
}
