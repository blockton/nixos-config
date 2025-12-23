{ inputs, ... }:
{
  imports = [ inputs.bongocat.nixosModules.default ];
  programs.wayland-bongocat = {
    enable = true;
    autostart = true;

    # Position
    catXOffset = 120; # Horizontal
    catYOffset = 0; # Vertical

    # Size (In pixels)
    catHeight = 40;
    overlayHeight = 30;

    # Animation settings
    fps = 60;
    idleFrame = 0;
    keypressDuration = 150; # (ms)
    enableHandMapping = true;

    # Visual
    overlayOpacity = 0;
    enableAntialiasing = true;

    inputDevices = [
      "/dev/input/event0"
      "/dev/input/event3"
      "/dev/input/event5"
      "/dev/input/event6"
      "/dev/input/event7"
      "/dev/input/event8"
      "/dev/input/event9"
      "/dev/input/event12"
      "/dev/input/event13"
    ];
    enableDebug = false;
  };
}
