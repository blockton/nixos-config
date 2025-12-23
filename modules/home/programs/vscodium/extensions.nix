{ pkgs, ... }:
let
  jonathanharty.gruvbox-material-icon-theme =
    pkgs.vscode-utils.buildVscodeMarketplaceExtension
      {
        mktplcRef = {
          name = "gruvbox-material-icon-theme";
          publisher = "JonathanHarty";
          version = "1.1.5";
          hash = "sha256-86UWUuWKT6adx4hw4OJw3cSZxWZKLH4uLTO+Ssg75gY=";
        };
      };
in
{
  programs.vscode.profiles.default = {
    extensions = with pkgs.vscode-extensions; [
      # Go
      golang.go

      # Py
      ms-python.python
      ms-python.pylint

      # Nix
      jnoortheen.nix-ide
      arrterian.nix-env-selector

      # Tools
      wakatime.vscode-wakatime
      # Formatters
      esbenp.prettier-vscode

      # Color scheme
      jdinhlife.gruvbox
      jonathanharty.gruvbox-material-icon-theme
    ];
  };
}
