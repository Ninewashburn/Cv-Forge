"""Erreurs métier, indépendantes du transport HTTP."""


class NotFoundError(Exception):
    """Entité absente ou soft-supprimée.

    Le message est celui que voit l'utilisateur (le frontend affiche ``detail``
    tel quel) : pas de nom de table ni d'identifiant, qui restent disponibles
    dans les attributs pour le journal."""

    def __init__(self, entity: str, entity_id: str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(
            "Cet élément n'existe plus (il a peut-être été supprimé). "
            "Actualise la page, puis réessaie."
        )
