let
  pkgs = import <nixpkgs> {};
in
  pkgs.callPackage ./package.nix { }
