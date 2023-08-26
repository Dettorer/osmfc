{
  description = "A tool that generates Anki or PDF flashcards from openstreetmap data";

  inputs = {
    # Use my own nixpkgs fork until the necessary python modules are available
    # and non-failing, see the following PRs:
    # - https://github.com/NixOS/nixpkgs/pull/230705
    # - https://github.com/NixOS/nixpkgs/pull/231735
    nixpkgs.url = "github:dettorer/nixpkgs/python-fixes";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: (
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python dependencies for building and using this project
        python-deps = (ps: with ps; [
          # genanki
          pandas # for geopandas (so that it can pull the correct libstdc++)
          numpy
          # TODO: package python-prettymaps in nixpkgs
        ]);

        # python-deps + extra dependencies used in the development process
        dev-python-deps = (ps:
          (python-deps ps) ++ (with ps; [
            anki
            aqt
            black
            jupyter
            mypy
          ])
        );
      in rec {
        devShells.default = pkgs.mkShell {
          nativeBuildInputs = with pkgs; [
            (python3.withPackages dev-python-deps)
            pre-commit
          ];
        };
      }
    )
  );
}
