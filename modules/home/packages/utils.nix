{ pkgs, ... }:
{
  home.packages = with pkgs; [
    # Archive Tools
    unzip # Extract ZIP archives

    # Better Core Utils
    duf # Disk information utility
    eza # Modern ls replacement
    fd # Find replacement
    hexyl # Hexadecimal viewer
    ripgrep # Fast search tool (grep replacement)

    # Development Utilities
    asciinema-agg # Convert asciinema recordings to GIF
    binsider # Analyze binaries for security
    bitwise # CLI tool for bit/hex manipulation
    entr # Run commands when files change
    hyperfine # Command-line benchmarking tool
    htop # Process viewer
    man-pages # Additional manual pages
    onefetch # Git repository information fetcher

    # System Monitoring
    wineWowPackages.waylandFull # Windows compatibility layer (Wayland)

    # Wayland Clipboard
    wl-clipboard # Clipboard utilities for Wayland (wl-copy, wl-paste)
  ];
}
