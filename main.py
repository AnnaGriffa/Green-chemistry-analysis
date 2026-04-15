def get_molecule():
    molecule = input("Enter molecule (e.g. H2O, CO2, NH3): ")
    return molecule.strip()

def main():
    mol = get_molecule()
    print(f"You entered: {mol}")

if __name__ == "__main__":
    main()