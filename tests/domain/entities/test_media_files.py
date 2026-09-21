import uuid

from app.domain.entities.media_files import MediaFile, MediaKind


class TestMediaFile:
    def test_create_minimal(self):
        owner_id = uuid.uuid4()

        media = MediaFile(
            owner_id=owner_id,
            storage_key="uploads/abc.jpg",
            mime_type="image/jpeg",
            media_kind=MediaKind.IMAGE,
            size_bytes=1024,
        )

        assert media.owner_id == owner_id
        assert media.storage_key == "uploads/abc.jpg"
        assert media.media_kind == MediaKind.IMAGE
        assert media.original_filename is None
        assert media.duration_ms is None

    def test_create_with_optional_fields(self):
        media = MediaFile(
            owner_id=uuid.uuid4(),
            storage_key="uploads/video.mp4",
            mime_type="video/mp4",
            media_kind=MediaKind.VIDEO,
            size_bytes=5_000_000,
            original_filename="clip.mp4",
            duration_ms=12_000,
            width=1920,
            height=1080,
            checksum_sha256="a" * 64,
        )

        assert media.original_filename == "clip.mp4"
        assert media.width == 1920
        assert media.height == 1080
        assert len(media.checksum_sha256) == 64

    def test_base_entity_fields(self):
        media = MediaFile(
            owner_id=uuid.uuid4(),
            storage_key="k",
            mime_type="image/png",
            media_kind=MediaKind.GIF,
            size_bytes=1,
        )

        assert media.id is not None
        assert media.created_at.tzinfo is not None
        assert media.updated_at.tzinfo is not None
