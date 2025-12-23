# Eza (ls replacement) configuration.

{
  programs.eza = {
    enable = true; # Enable eza as ls replacement

    git = true; # Show git status indicators
    colors = "always"; # Always use colors for output
    icons = "always"; # Always show file type icons
    enableZshIntegration = true; # Enable Zsh shell integration
    # Additional command-line options
    extraOptions = [
      "--group-directories-first" # List directories before files
      "--header" # Show header with column names
    ];
  };
}
