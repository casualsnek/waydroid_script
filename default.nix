with (import <nixpkgs> {});

stdenv.mkDerivation {
  name = "waydroid_script";

  buildInputs = [
    (python3.withPackages(ps: with ps; [ tqdm requests inquirerpy ]))
  ];

  src = ./.;

  postPatch = ''
    patchShebangs main.py
  '';

  installPhase = ''
    mkdir -p $out/libexec
    cp -r . $out/libexec/waydroid_script
    mkdir -p $out/bin
    ln -s $out/libexec/waydroid_script/main.py $out/bin/waydroid_script
  '';
}
