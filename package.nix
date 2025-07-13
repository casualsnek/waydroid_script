{ lib,
  stdenvNoCC,
  lzip,
  python3,
  makeWrapper }:
let
  wrappedPath = lib.makeBinPath [ lzip ];
in stdenvNoCC.mkDerivation {
  name = "waydroid_script";

  buildInputs = [
    (python3.withPackages(ps: with ps; [ tqdm requests inquirerpy ]))
  ];

  nativeBuildInputs = [
    makeWrapper
  ];

  src = ./.;

  postPatch = ''
    patchShebangs main.py
  '';

  installPhase = ''
    mkdir -p $out/libexec
    cp -r . $out/libexec/waydroid_script
    mkdir -p $out/bin
    makeShellWrapper $out/libexec/waydroid_script/main.py $out/bin/waydroid_script \
      --prefix PATH : "${wrappedPath}"
  '';
}
