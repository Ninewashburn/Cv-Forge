"""Erreurs métier, indépendantes du transport HTTP."""


class NotFoundError(Exception):
    """Entité absente ou soft-supprimée."""

    def __init__(self, entity: str, entity_id: str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} introuvable : {entity_id}")
