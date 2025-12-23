{ pkgs, ... }:
{
  home.packages = with pkgs; [
    broot # Tree file viewer with fuzzy search
    epy # Terminal ebook reader
    gtt # Google Translate TUI client
    ncdu # Disk space analyzer with ncurses interface
    programmer-calculator # Calculator for programmers
    tdf # Terminal-based PDF viewer
    toipe # Typing test in the terminal
    ttyper # CLI typing test application
  ];
}
