{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pandas
  ];

  # Optionally, create a virtual environment and activate it
  shellHook = ''
    if [ ! -d .venv ]; then
      python -m venv .venv
      . .venv/bin/activate
      pip install --upgrade pip
    fi
    source .venv/bin/activate
  '';
}
