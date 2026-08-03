from abc import ABC

from src.domain.entities.design_assets import DesignAsset
from src.domain.repository.base import BaseRepository


class BaseDesignAssetsRepository(BaseRepository[DesignAsset], ABC):
    pass
