from pathlib import Path
from click import confirm
import sys
import numpy as np

from h5py import File
import pandas as pd
import ase
from ase.neighborlist import neighbor_list


from progbar import ProgBar


class DataPreprocesser:
    """
    Class that contains the methods necessary to perform the
    following preprocessing steps:

        - Extract data from the base `OCH.h5` file  
        - Explode the data to include an entry for every conformation
        - (TODO) One-hot encode pair-wise distance atomic pair relations
        - (TODO) Replace the atomic_configuration data for each conformation
            with pairwise distances between atoms
        - (TODO) Annotate bond pairs (how to relate to pairwise distances?
        maybe increase number of one-hot categories to included bonded/non-bonded)
        - Chunkily load the data to the `OCH_ext.h5` file.
    """

    def __init__(self, data_path: Path, out_path: Path, *, chunksize: int):
        self.data_path = data_path
        self.out_path = out_path
        self.chunksize = chunksize
        self.one_cols = [
            "atomic_numbers",
            "smiles",
        ]  # Columns consistent across all conformations
        self.atom_num_map = {8:"O", 6: "C", 1:"H"}
        self.params = { #TODO: Implement this in a dtoenv file
            "cutoff_r": 2.5
        }

    def __call__(self):
        self.validate()
        self.load()

    def validate(self):
        assert Path(
            self.data_path
        ).exists(), f"Requested input data path ({self.data_path}) does not exist!"
        if Path(self.out_path).exists():
            if confirm(
                f"Detected existing file at {self.out_path}, would you like to delete and continue?",
                default=False,
            ):
                self.out_path.unlink()
            else:
                sys.exit(f"Chose to keep existing preprocessed data at {self.out_path}")

        with File(self.data_path, "r") as ff:
            # Check that chunksize divides the number of conformations
            vals = list(ff.values())
            n_mols = len(vals)
            n_confs = vals[0]["conformations"][()].shape[0]
            assert (
                not n_confs * n_mols % self.chunksize
            ), f"Pick chunksize that divides {n_confs*n_mols}"

    def create_schema(self, file: File) -> tuple:
        cols = [col for col in list(file.values())[0].keys() if col != "subset"]
        inds = (
            []
        )  # Indices for each row, corresponding to a molecule index and conformation number
        mols = list(file.keys())  # Indices for individual molecules
        for mol in mols:
            conformations = file[f"{mol}/conformations"].shape[0]
            for i in range(conformations):
                inds.append(f"{mol}/{i}")
        return (cols, inds)

    def interatomic_distances(self, conformation: np.ndarray) -> np.ndarray:
        """ 
        Take the 3D conformation and convert to pairwise displacements for each atom. 
        Return the double indices of atoms
        """
        _a = ase.Atoms(positions=conformation, pbc=True)
        i, j, d = neighbor_list("ijd", _a, cutoff=self.params["cutoff_r"])
        return (np.array(list(zip(i, j))), d)

    def one_hot_pairwise(self, atomic_numbers):
        pass

    def annotate_bonds(self, smile_string: str):
        pass

    def load(self):
        chunk_size = self.chunksize
        current_chunk = 0
        with File(self.data_path, "r") as f:
            cols, inds = self.create_schema(f)
            n_chunks = len(inds) // chunk_size
            prg = ProgBar(n_chunks)
            while True:
                prg.update(current_chunk)
                if current_chunk >= len(inds) // chunk_size:
                    break
                _inds = inds[
                    current_chunk * chunk_size : (current_chunk + 1) * chunk_size
                ]
                df = pd.DataFrame(columns=cols, index=_inds)
                for _ind in _inds:
                    for col in cols:
                        # Case where column has distinct value for each conformation
                        try:
                            mol, i = _ind.split("/")
                            if col not in self.one_cols:
                                df.loc[_ind][col] = f[f"{mol}/{col}"][()][int(i)]
                            else:
                                df.loc[_ind][col] = f[f"{mol}/{col}"][()]
                        except KeyError:
                            pass
                df.to_hdf(self.out_path, key=f"chunk_{current_chunk}")
                current_chunk += 1


if __name__ == "__main__":
    in_path = Path(__file__).parent.parent.parent / "data" / "raw" / "OCH.h5"
    out_path = Path(__file__).parent.parent.parent / "data" / "processed" / "OCH_ext_test1.h5"

    etl = DataPreprocesser(in_path, out_path, chunksize=1000)
    # etl()
    df = pd.read_hdf(out_path, "chunk_0")
    print(etl.interatomic_distances(df.iloc[0].conformations))
