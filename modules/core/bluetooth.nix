{
  # Bluetooth hardware configuration
  hardware.bluetooth = {
    enable = true;
    powerOnBoot = true;
    settings = {
      General = {
        # Enable various Bluetooth profiles
        Enable = "Source,Sink,Media,Socket";
        Experimental = true; # Enable experimental features
      };
    };
  };
  # Blueman Bluetooth manager GUI
  services.blueman.enable = true;
}
