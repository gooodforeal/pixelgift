from abc import ABC

from app.domain.entities.design_assets import DesignAsset
from app.domain.repository.base import BaseRepository


class BaseDesignAssetsRepository(BaseRepository[DesignAsset], ABC):
    pass
