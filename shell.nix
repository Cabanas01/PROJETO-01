{
  pkgs ? import <nixpkgs> { },
}: pkgs.mkShell {
  buildInputs = [pkgs.python311 pkgs.python311Packages.flask pkgs.python311Packages.flask-cors ];
}

