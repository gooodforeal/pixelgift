from app.application.use_cases.media import resolve_media_kind
from app.domain.entities.media_files import MediaKind
from app.domain.exceptions.media_files import UnsupportedMediaTypeError
import pytest


class TestResolveMediaKind:
    def test_audio_mp3_alias(self):
        kind, mime = resolve_media_kind("audio/mp3", "note.mp3")
        assert kind == MediaKind.VOICE
        assert mime == "audio/mpeg"

    def test_extension_when_octet_stream(self):
        kind, mime = resolve_media_kind(
            "application/octet-stream", "voice-message.ogg"
        )
        assert kind == MediaKind.VOICE
        assert mime == "audio/ogg"

    def test_preferred_voice_for_webm(self):
        kind, mime = resolve_media_kind(
            "video/webm",
            "rec.webm",
            preferred_kind=MediaKind.VOICE,
        )
        assert kind == MediaKind.VOICE
        assert mime == "audio/webm"


    def test_quicktime_mov_is_video(self):
        kind, mime = resolve_media_kind("video/quicktime", "clip.mov")
        assert kind == MediaKind.VIDEO
        assert mime == "video/quicktime"

    def test_mov_extension_when_octet_stream(self):
        kind, mime = resolve_media_kind("application/octet-stream", "clip.mov")
        assert kind == MediaKind.VIDEO
        assert mime == "video/quicktime"

    def test_preferred_rejects_mismatch(self):
        with pytest.raises(UnsupportedMediaTypeError):
            resolve_media_kind(
                "image/png",
                "photo.png",
                preferred_kind=MediaKind.VOICE,
            )

    def test_unknown_without_extension_raises(self):
        with pytest.raises(UnsupportedMediaTypeError):
            resolve_media_kind("application/octet-stream", "file")
