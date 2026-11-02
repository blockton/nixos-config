#=====================================================================#
# MACHINE CONFIGURATION (ASPIRE)
#=====================================================================#
#- NixOS settings that belong to this computer alone (hardware, power and
#- the like). On/off switches go in settings.nix beside this file, and each
#- person's apps in users/<username>/settings.nix.
{
  lib,
  machine,
  ...
}: {
  #--------------------------------------------------------------------#
  #-- Machine Settings
  #--------------------------------------------------------------------#
  #--- DMS's bar menu switches profiles through this system service
  services.power-profiles-daemon.enable = true;

  #--------------------------------------------------------------------#
  #-- Imports
  #--------------------------------------------------------------------#
  imports =
    [
      #--- Disks and kernel modules, from `nixos-generate-config`
      ./hardware/hardware-configuration.nix

      ../../modules
    ]
    #--- Disk-unlock lines setup.sh copied from the installer's configuration.nix
    ++ lib.optional (builtins.pathExists ./hardware/boot.nix) ./hardware/boot.nix
    ++ (lib.optional (machine.windowManager == "niri") ./wm/niri.nix);
}
