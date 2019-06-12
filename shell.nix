with import <nixpkgs> {};

stdenv.mkDerivation {
    name = "hanadb_exporter";

    buildInputs = [
        (python2.withPackages (ps: [ps.tox ps.pip]))
        (python3.withPackages (ps: [ps.tox ps.pip]))
    ];
}

