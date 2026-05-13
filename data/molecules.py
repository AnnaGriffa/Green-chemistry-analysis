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
PUBCHEM_VIEW_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
OUTPUT_PATH = Path(__file__).with_name("molecule_datas.json")
IMAGES_DIR = Path(__file__).with_name("images")
PUBCHEM_PROPERTIES = [
    "CID",
    "MolecularFormula",
    "MolecularWeight",
]
GHS_PICTOGRAMS = [
    {
        "code": "GHS01",
        "name": "Exploding Bomb",
        "keywords": ["Explosive", "Exploding Bomb", "GHS01"],
    },
    {
        "code": "GHS02",
        "name": "Flame",
        "keywords": ["Flammable", "Flame", "GHS02"],
    },
    {
        "code": "GHS03",
        "name": "Flame Over Circle",
        "keywords": ["Oxidizer", "Oxidizing", "Flame Over Circle", "GHS03"],
    },
    {
        "code": "GHS04",
        "name": "Gas Cylinder",
        "keywords": ["Compressed Gas", "Gas Cylinder", "GHS04"],
    },
    {
        "code": "GHS05",
        "name": "Corrosion",
        "keywords": ["Corrosive", "Corrosion", "GHS05"],
    },
    {
        "code": "GHS06",
        "name": "Skull and Crossbones",
        "keywords": ["Acute Toxic", "Skull and Crossbones", "GHS06"],
    },
    {
        "code": "GHS07",
        "name": "Exclamation Mark",
        "keywords": ["Irritant", "Exclamation Mark", "GHS07"],
    },
    {
        "code": "GHS08",
        "name": "Health Hazard",
        "keywords": ["Health Hazard", "GHS08"],
    },
    {
        "code": "GHS09",
        "name": "Environmental Hazard",
        "keywords": ["Environmental Hazard", "Environment", "GHS09"],
    },
]


@dataclass(frozen=True)
class MoleculeInfo:
    name: str
    cid: int
    formula: str
    atom_count: int
    molar_mass: float
    molecule_image_path: str
    ghs_pictograms: list[dict[str, str]]


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


def download_molecule_image(cid: int, molecule_name: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", molecule_name.strip()).strip("_")
    image_path = IMAGES_DIR / f"{safe_name or cid}_{cid}.png"
    url = (
        f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/PNG"
        "?record_type=2d&image_size=large"
    )

    try:
        with urlopen(url, timeout=15) as response:
            image_data = response.read()
    except HTTPError as error:
        raise ValueError(
            f"PubChem n'a pas pu generer l'image du CID {cid}."
        ) from error
    except URLError as error:
        raise ConnectionError(
            f"Impossible de telecharger l'image PubChem du CID {cid}: {error.reason}"
        ) from error

    IMAGES_DIR.mkdir(exist_ok=True)
    image_path.write_bytes(image_data)
    return image_path


def fetch_pubchem_view_ghs_classification(cid: int) -> dict[str, object] | None:
    url = f"{PUBCHEM_VIEW_BASE_URL}/data/compound/{cid}/JSON?heading=GHS+Classification"

    try:
        with urlopen(url, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise ValueError(
            f"PubChem n'a pas pu recuperer la classification GHS du CID {cid}."
        ) from error
    except URLError as error:
        raise ConnectionError(
            f"Impossible de joindre PubChem PUG-View pour le CID {cid}: {error.reason}"
        ) from error


def iter_strings(value: object) -> list[str]:
    strings = []

    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        for item in value.values():
            strings.extend(iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(iter_strings(item))

    return strings


def extract_ghs_pictograms(
    pubchem_view_data: dict[str, object] | None,
) -> list[dict[str, str]]:
    if not pubchem_view_data:
        return []

    all_strings = iter_strings(pubchem_view_data)
    found_pictograms = []

    for pictogram in GHS_PICTOGRAMS:
        keywords = pictogram["keywords"]
        if any(
            keyword.lower() in text.lower()
            for keyword in keywords
            for text in all_strings
        ):
            code = pictogram["code"]
            found_pictograms.append(
                {
                    "code": code,
                    "name": pictogram["name"],
                    "image_url": f"https://pubchem.ncbi.nlm.nih.gov/images/ghs/{code}.gif",
                }
            )

    return found_pictograms


def get_molecule_info(molecule_name: str) -> MoleculeInfo:
    pubchem_data = fetch_pubchem_properties_by_name(molecule_name)
    cid = int(pubchem_data["CID"])
    formula = str(pubchem_data["MolecularFormula"])
    image_path = download_molecule_image(cid, molecule_name)
    ghs_data = fetch_pubchem_view_ghs_classification(cid)

    return MoleculeInfo(
        name=molecule_name,
        cid=cid,
        formula=formula,
        atom_count=count_atoms_from_formula(formula),
        molar_mass=float(pubchem_data["MolecularWeight"]),
        molecule_image_path=str(image_path),
        ghs_pictograms=extract_ghs_pictograms(ghs_data),
    )


def save_molecule_info_to_json(
    molecule_info: MoleculeInfo,
    output_path: Path = OUTPUT_PATH,
) -> None:
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
    else:
        existing = {}

    existing[molecule_info.name] = asdict(molecule_info)

    output_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
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
