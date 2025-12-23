{ pkgs, ... }:
{
  home.packages = with pkgs; [
    # Audio/Media Tools
    spotify
    audacity # Audio editor and recorder
    pavucontrol # PulseAudio volume control
    soundwireserver # Audio streaming server
    video-trimmer # Simple video trimming tool
    vlc # Media player

    # Browsers
    chromium # Web browser
    tor-browser # Tor anonymity browser

    # Development Tools
    claude-code # Claude AI CLI tool
    ldtk # Level designer toolkit for 2D games
    tiled # Tile map editor

    # Games & Entertainment
    termius # SSH client (moved here as it's GUI-based)

    # Graphics
    gimp # GNU Image Manipulation Program

    # Network/VPN
    mullvad-vpn # Mullvad VPN client
    protonvpn-gui # ProtonVPN GUI client

    # Office/Productivity
    gnome-calculator # Calculator application
    libreoffice # Office suite

    # System Utilities
    dconf-editor # Configuration system editor
    gnome-disk-utility # Disk management tool
    mission-center # GUI resources monitor
    zenity # GTK dialog boxes

    # Updates
    wasistlos # What's Out? (updates checker)

    # Communication
    telegram-desktop # Telegram messenger

    # Media Downloading
    media-downloader # Media download manager
    obs-studio # Open Broadcaster Software
  ];
}
