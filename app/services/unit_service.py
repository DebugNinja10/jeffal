UNIT_ALIASES = {
    "kg": "kg",
    "kilo": "kg",
    "kilos": "kg",
    "kilogramme": "kg",
    "kilogrammes": "kg",

    "g": "g",
    "gramme": "g",
    "grammes": "g",

    "l": "litre",
    "litre": "litre",
    "litres": "litre",

    "sac": "sac",
    "sacs": "sac",

    "unité": "unité",
    "unités": "unité",
    "unite": "unité",
    "unites": "unité",
}


def normalize_unit(unit: str) -> str:
    """
    Normalise une unité exprimée naturellement par l'utilisateur.

    Exemples :
    kilo -> kg
    kilos -> kg
    sacs -> sac
    litres -> litre
    """

    normalized = unit.strip().lower()

    return UNIT_ALIASES.get(
        normalized,
        normalized,
    )


def convert_to_base_unit(
    quantity: float,
    sold_unit: str,
    base_unit: str,
    package_size: float | None = None,
) -> float:
    """
    Convertit une quantité vendue vers l'unité de base.

    Exemple :
    1 sac de riz avec package_size=25 et base_unit=kg
    devient 25 kg.

    Les variantes naturelles d'une unité sont d'abord
    normalisées.

    Exemple :
    0,5 kilo -> 0,5 kg
    """

    sold_unit = normalize_unit(sold_unit)
    base_unit = normalize_unit(base_unit)

    if quantity <= 0:
        raise ValueError(
            "La quantité doit être supérieure à zéro."
        )

    # Aucune conversion nécessaire.
    if sold_unit == base_unit:
        return quantity

    if package_size is None or package_size <= 0:
        raise ValueError(
            f"Impossible de convertir '{sold_unit}' "
            f"vers '{base_unit}' sans package_size valide."
        )

    return quantity * package_size
