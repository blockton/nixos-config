{
  pkgs,
  user,
  host,
  inputs,
  system,
  pkgsStable,
  userSettings,
  ...
}:
{
  imports = [ inputs.home-manager.nixosModules.home-manager ];
  home-manager = {
    useGlobalPkgs = true;
    useUserPackages = true;
    extraSpecialArgs = {
      inherit
        user
        host
        inputs
        system
        pkgsStable
        userSettings
        ;
    };
    users.${user} = {
      imports =
        if (host == "desktop") then [ ./../home/default.nix ] else [ ./../home ];
      #home.user = "${user}";
      home.stateVersion = "25.05";
      home.homeDirectory = "/home/${user}";
      programs.home-manager.enable = true;
    };
    backupFileExtension = "hm-backup";
  };

  users.users.${user} = {
    isNormalUser = true;
    description = "${user}";
    extraGroups = [
      "networkmanager"
      "wheel"
      "input"
    ];
    shell = pkgs.zsh;
  };
  nix.settings.allowed-users = [ "${user}" ];
}
