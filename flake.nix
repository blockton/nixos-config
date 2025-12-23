{
  description = "Wael's nixos configuration";

  inputs = {
    nur.url = "github:nix-community/NUR";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs-stable.url = "github:nixos/nixpkgs/nixos-25.05";

    vicinae.url = "github:vicinaehq/vicinae";
    bongocat.url = "github:saatvik333/wayland-bongocat";
    superfile.url = "github:yorukot/superfile";
    nix-gaming.url = "github:fufexan/nix-gaming";
    nix-flatpak.url = "github:gmodena/nix-flatpak";
    zen-browser.url = "github:0xc000022070/zen-browser-flake/beta";

    sops-nix = {
      url = "github:Mic92/sops-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    maple-mono = {
      url = "github:subframe7536/maple-font/variable";
      flake = false;
    };

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    nix-index-database = {
      url = "github:nix-community/nix-index-database";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      nixpkgs-stable,
      sops-nix,
      ...
    }@inputs:
    let
      user = "w";
      system = "x86_64-linux";
      userSettings = {
        gitConfig = {
          name = "blockton";
          email = "blockton.dev@gmail.com";
          signingKey = "13E1D256F8E8BCFF";
        };
      };
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          allowBroken = false;
          allowInsecure = false;
          allowUnsupportedSystem = false;
        };
      };
      pkgsStable = import nixpkgs-stable {
        inherit system;
        config = {
          allowUnfree = true;
          allowBroken = false;
          allowInsecure = false;
          allowUnsupportedSystem = false;
        };
      };
    in
    {
      nixosConfigurations = {
        laptop = nixpkgs.lib.nixosSystem {
          inherit system;
          modules = [ ./hosts/laptop ];
          specialArgs = {
            host = "laptop";
            inherit
              self
              user
              inputs
              system
              pkgsStable
              userSettings
              ;
          };
        };
        desktop = nixpkgs.lib.nixosSystem {
          inherit system;
          modules = [ ./hosts/desktop ];
          specialArgs = {
            host = "desktop";
            inherit
              self
              user
              inputs
              system
              pkgsStable
              userSettings
              ;
          };
        };
        vm = nixpkgs.lib.nixosSystem {
          inherit system;
          modules = [ ./hosts/vm ];
          specialArgs = {
            host = "vm";
            inherit
              self
              user
              inputs
              system
              pkgsStable
              userSettings
              ;
          };
        };
      };
    };
}
