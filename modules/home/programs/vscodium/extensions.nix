{ pkgs, ... }:
let
  natizyskunk.sftp = pkgs.vscode-utils.buildVscodeMarketplaceExtension {
    mktplcRef = {
      name = "sftp";
      hash = "sha256-HifPiHIbgsfTldIeN9HaVKGk/ujaZbjHMiLAza/o6J4=";
      version = "1.16.3";
      publisher = "natizyskunk";
    };
  };
  ionutvmi.path-autocomplete = pkgs.vscode-utils.buildVscodeMarketplaceExtension {
    mktplcRef = {
      name = "path-autocomplete";
      hash = "sha256-iz32o1znwKpbJSdrDYf+GDPC++uGvsCdUuGaQu6AWEo=";
      version = "1.25.0";
      publisher = "ionutvmi";
    };
  };
  tldraw-org.tldraw-vscode = pkgs.vscode-utils.buildVscodeMarketplaceExtension {
    mktplcRef = {
      name = "tldraw-vscode";
      hash = "sha256-h5OpIH4l2QJonb5pk5RxGYPiSX/zPXPs6OZPZi6Dor8=";
      version = "2.199.1";
      publisher = "tldraw-org";
    };
  };
  jonathanharty.gruvbox-material-icon-theme = pkgs.vscode-utils.buildVscodeMarketplaceExtension {
    mktplcRef = {
      name = "gruvbox-material-icon-theme";
      hash = "sha256-86UWUuWKT6adx4hw4OJw3cSZxWZKLH4uLTO+Ssg75gY=";
      version = "1.1.5";
      publisher = "JonathanHarty";
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
      natizyskunk.sftp
      tldraw-org.tldraw-vscode
      wakatime.vscode-wakatime
      ionutvmi.path-autocomplete

      # Formatters
      esbenp.prettier-vscode

      # Color scheme
      jdinhlife.gruvbox
      jonathanharty.gruvbox-material-icon-theme
    ];
  };
}
