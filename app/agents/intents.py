from enum import Enum


class IntentName(str, Enum):
    ENREGISTRER_VENTE = "enregistrer_vente"
    ENREGISTRER_DEPENSE = "enregistrer_depense"
    ENREGISTRER_DETTE = "enregistrer_dette"
    ENREGISTRER_REMBOURSEMENT = "enregistrer_remboursement"
    CONSULTER_STOCK = "consulter_stock"
    ANALYSER_ACTIVITE = "analyser_activite"
    UNKNOWN = "unknown"
