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
    """

    sold_unit = sold_unit.strip().lower()
    base_unit = base_unit.strip().lower()

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
