with import <nixpkgs> {};
with pkgs.python27Packages;

stdenv.mkDerivation {
  name = "impurePythonEnv";
  buildInputs = [
    python27Full
    python27Packages.virtualenv
    python27Packages.pip
  ];
  src = null;
  shellHook = ''
    # set SOURCE_DATE_EPOCH so that we can use python wheels
    SOURCE_DATE_EPOCH=$(date +%s)
    virtualenv --no-setuptools venv
    export PATH=$PWD/venv/bin:$PATH
    pip install -r requirements.txt
  '';
}

