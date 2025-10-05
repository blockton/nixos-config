{
  description = "My system configuration";

  inputs = {

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nixpkgs-stable.url = "github:nixos/nixpkgs/nixos-25.05";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

  };

  outputs =
    {
      self,
      nixpkgs,
      nixpkgs-stable,
      home-manager,
      ...
    }@inputs:

    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      pkgs-stable = import nixpkgs-stable {
        inherit system;
        config.allowUnfree = true;
      };
    in
    {
      # nixos - system hostname
      nixosConfigurations.nixos = nixpkgs.lib.nixosSystem {
        specialArgs = { inherit inputs system pkgs-stable; };
        modules = [ ./nixos/configuration.nix ];
      };

      homeConfigurations.w = home-manager.lib.homeManagerConfiguration {
        extraSpecialArgs = { inherit inputs system pkgs-stable; };
        pkgs = nixpkgs.legacyPackages.${system};
        modules = [ ./home/home.nix ];
      };
    };
}
