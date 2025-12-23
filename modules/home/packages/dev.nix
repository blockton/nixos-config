{ pkgs, ... }:
{
  home.packages = with pkgs; [
    # Build Systems
    cmake # Cross-platform build system
    gnumake # GNU make utility

    # C/C++ Tools
    gcc # GNU Compiler Collection
    gdb # GNU Debugger
    gef # GDB Enhanced Features
    llvmPackages_20.clang-tools # Clang compiler tools
    valgrind # Memory debugging and profiling tool

    # Formatting
    nixfmt-rfc-style # Nix formatter following RFC style
    shfmt # Shell script formatter
    treefmt # Project-wide code formatter

    # Language Servers
    nixd # Nix language server
  ];
}
