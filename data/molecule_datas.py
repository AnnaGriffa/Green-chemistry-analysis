from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
OUTPUT_PATH = Path(__file__).with_name("molecule_datas.json")
PUBCHEM_PROPERTIES = [
    "MolecularFormula",
    "MolecularWeight",
]


@dataclass(frozen=True)
class MoleculeInfo:
    name: str
    formula: str
    atom_count: int
    molar_mass: float


def count_atoms_from_formula(formula: str) -> int:
    """Count atoms from a molecular formula such as C9H8O4 or NaCl."""
    total_atoms = 0
    tokens = re.findall(r"([A-Z][a-z]?)(\d*)", formula)

    for _element, count in tokens:
        total_atoms += int(count) if count else 1

    return total_atoms


def fetch_pubchem_properties_by_name(molecule_name: str) -> dict[str, object]:
    encoded_name = quote(molecule_name, safe="")
    properties = ",".join(PUBCHEM_PROPERTIES)
    url = (
        f"{PUBCHEM_BASE_URL}/compound/name/{encoded_name}"
        f"/property/{properties}/JSON"
    )

    try:
        with urlopen(url, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise ValueError(
            f"PubChem n'a pas trouve de molecule nommee '{molecule_name}'."
        ) from error
    except URLError as error:
        raise ConnectionError(
            f"Impossible de joindre PubChem pour '{molecule_name}': {error.reason}"
        ) from error

    compounds = payload.get("PropertyTable", {}).get("Properties", [])
    if not compounds:
        raise ValueError(f"PubChem n'a retourne aucune donnee pour '{molecule_name}'.")

    return compounds[0]


def get_molecule_info(molecule_name: str) -> MoleculeInfo:
    pubchem_data = fetch_pubchem_properties_by_name(molecule_name)
    formula = str(pubchem_data["MolecularFormula"])

    return MoleculeInfo(
        name=molecule_name,
        formula=formula,
        atom_count=count_atoms_from_formula(formula),
        molar_mass=float(pubchem_data["MolecularWeight"]),
    )


def save_molecule_info_to_json(
    molecule_info: MoleculeInfo,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output_path.write_text(
        json.dumps(asdict(molecule_info), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    molecule_name = " ".join(sys.argv[1:]).strip()
    if not molecule_name:
        molecule_name = input("Nom de la molecule: ").strip()

    try:
        molecule_info = get_molecule_info(molecule_name)
    except (ConnectionError, ValueError) as error:
        print(error)
        raise SystemExit(1) from error

    save_molecule_info_to_json(molecule_info)
    print(f"Donnees enregistrees dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
