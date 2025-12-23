{
  programs.vscode.profiles.default = {
    userSettings = {
      "update.mode" = "none";
      "extensions.autoUpdate" = false; # This stuff fixes vscode freaking out when theres an update
      "window.titleBarStyle" = "custom"; # needed otherwise vscode crashes, see https://github.com/NixOS/nixpkgs/issues/246509

      "window.menuBarVisibility" = "toggle";
      "editor.fontFamily" = "'Maple Mono', 'SymbolsNerdFont', 'monospace', monospace";
      "terminal.integrated.fontFamily" = "'Maple Mono', 'SymbolsNerdFont'";

      "workbench.colorTheme" = "Gruvbox Dark Hard";
      "workbench.iconTheme" = "gruvbox-material-icon-theme";
      "material-icon-theme.folders.theme" = "classic";
      "vsicons.dontShowNewVersionMessage" = true;
      "explorer.confirmDragAndDrop" = false;

      "editor.fontSize" = 18;
      "editor.formatOnSave" = true;
      "editor.formatOnType" = true;
      "editor.formatOnPaste" = true;
      "editor.fontLigatures" = true;
      "editor.mouseWheelZoom" = true;
      "editor.inlayHints.enabled" = "off";

      "editor.scrollbar.vertical" = "visible";
      "editor.scrollbar.horizontal" = "visible";
      "editor.scrollbar.verticalScrollbarSize" = 2;
      "editor.scrollbar.horizontalScrollbarSize" = 2;

      "files.autoSave" = "onWindowChange";
      "files.insertFinalNewline" = true;

      # C/C++
      "clangd.arguments" = [
        "--clang-tidy"
        "--inlay-hints=false"
      ];

      # nix
      "nix.serverPath" = "nixd";
      "nix.enableLanguageServer" = true;
    };
  };
}
