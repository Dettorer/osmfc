{
  description = "A tool that generates Anki or PDF flashcards from openstreetmap data";

  inputs = {
    # Use my own nixpkgs fork until the anki and aqt python modules are merged
    # into nixpkgs (https://github.com/NixOS/nixpkgs/pull/230705)
    nixpkgs.url = "github:dettorer/nixpkgs/python-add-anki";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: (
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python dependencies for building and using this project
        python-deps = (ps: with ps; [ osmpythontools pyosmium ]);

        # python-deps + extra dependencies used in the development process
        dev-python-deps = (ps:
          (python-deps ps) ++ (with ps; [ anki aqt black mypy ])
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
