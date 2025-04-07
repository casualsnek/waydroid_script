{
  description = "Waydroid Extras Script";
  inputs = {
    systems.url = "github:nix-systems/default";
  };
  outputs = { self, nixpkgs, systems }:
  let
    inherit (nixpkgs) lib;
    eachSystem = lib.genAttrs (import systems);
    mkApp = program: { type = "app"; inherit program; };
  in {
    packages = eachSystem (system: rec {
      waydroid_script = nixpkgs.legacyPackages."${system}".callPackage ./package.nix { };
      default = waydroid_script;
    });
    apps = eachSystem (system: rec {
      waydroid_script = mkApp "${self.outputs.packages.${system}.waydroid_script}/bin/waydroid_script";
      default = waydroid_script;
    });
  };
}
