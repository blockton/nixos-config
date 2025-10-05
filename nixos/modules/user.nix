{ pkgs, ... }:
{
  programs.zsh.enable = true;

  users = {
    defaultUserShell = pkgs.zsh;

    users.w = {
      isNormalUser = true;
      description = "w";
      extraGroups = [
        "networkmanager"
        "wheel"
        "input"
        "libvirtd"
      ];
      packages = with pkgs; [ ];
    };
  };

  # Enable automatic login for the user.
  services.getty.autologinUser = "w";
}
