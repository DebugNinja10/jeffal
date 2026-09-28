from app.agents.intents import IntentName
from app.agents.mock_intent_parser import MockIntentParser


def test_vente_boutique():
    parser = MockIntentParser()

    result = parser.parse("j'ai vendu 2 kilos de riz")

    assert result.intent == IntentName.ENREGISTRER_VENTE
    assert result.needs_clarification is False
    assert result.data["items"][0]["product_name"] == "riz"
    assert result.data["items"][0]["quantity"] == 2.0


def test_vente_cosmetique():
    parser = MockIntentParser()

    result = parser.parse("j'ai vendu 2 parfums")

    assert result.intent == IntentName.ENREGISTRER_VENTE
    assert result.needs_clarification is False
    assert result.data["items"][0]["product_name"] == "parfums"
    assert result.data["items"][0]["quantity"] == 2.0


def test_vente_multiservice():
    parser = MockIntentParser()

    result = parser.parse("j'ai vendu 3 écouteurs")

    assert result.intent == IntentName.ENREGISTRER_VENTE
    assert result.needs_clarification is False
    assert result.data["items"][0]["product_name"] == "écouteurs"
    assert result.data["items"][0]["quantity"] == 3.0


def test_vente_vetements():
    parser = MockIntentParser()

    result = parser.parse("j'ai vendu 2 robes")

    assert result.intent == IntentName.ENREGISTRER_VENTE
    assert result.needs_clarification is False
    assert result.data["items"][0]["product_name"] == "robes"
    assert result.data["items"][0]["quantity"] == 2.0


def test_vente_multi_produits():
    parser = MockIntentParser()

    result = parser.parse(
        "j'ai vendu 2 kilos de riz et 3 bouteilles d'huile"
    )

    assert result.intent == IntentName.ENREGISTRER_VENTE
    assert result.needs_clarification is False
    assert len(result.data["items"]) == 2


def test_depense():
    parser = MockIntentParser()

    result = parser.parse("j'ai dépensé 5000 pour acheter des marchandises")

    assert result.intent == IntentName.ENREGISTRER_DEPENSE
    assert result.needs_clarification is False
    assert result.data["amount"] == 5000.0


def test_dette():
    parser = MockIntentParser()

    result = parser.parse("Moussa me doit 5000")

    assert result.intent == IntentName.ENREGISTRER_DETTE
    assert result.needs_clarification is False
    assert result.data["customer_name"] == "moussa"
    assert result.data["amount"] == 5000.0


def test_remboursement():
    parser = MockIntentParser()

    result = parser.parse("j'ai remboursé 3000 à Moussa")

    assert result.intent == IntentName.ENREGISTRER_REMBOURSEMENT
    assert result.needs_clarification is False
    assert result.data["customer_name"] == "moussa"
    assert result.data["amount"] == 3000.0


def test_consultation_stock():
    parser = MockIntentParser()

    result = parser.parse("combien me reste de parfum")

    assert result.intent == IntentName.CONSULTER_STOCK
    assert result.needs_clarification is False
    assert result.data["product_name"] == "parfum"
