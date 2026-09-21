from io import BytesIO
from functools import lru_cache
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.application.ports.certificates.base import (
    BaseGiftCertificateRenderer,
    CertificateTheme,
    GiftCertificateData,
)

_VIOLET = HexColor("#a855f7")
_PINK = HexColor("#f472b6")
_CYAN = HexColor("#22d3ee")
_GOLD = HexColor("#fbbf24")

_GRADIENT = ("#f472b6", "#a855f7", "#22d3ee")
_FONTS_DIR = Path(__file__).resolve().parents[2] / "static" / "fonts"
_UNBOUNDED_EXTRABOLD = _FONTS_DIR / "Unbounded-ExtraBold.ttf"
_UNBOUNDED_BOLD = _FONTS_DIR / "Unbounded-Bold.ttf"


class _Palette:
    __slots__ = (
        "bg",
        "bg_soft",
        "card",
        "text",
        "muted",
        "accent",
        "frame_outer",
        "frame_inner",
        "blob_alpha",
        "footer",
        "qr_fg",
        "pixel_rgb",
    )

    def __init__(
        self,
        *,
        bg: HexColor,
        bg_soft: HexColor,
        card: HexColor,
        text: HexColor,
        muted: HexColor,
        accent: HexColor,
        frame_outer: HexColor,
        frame_inner: HexColor,
        blob_alpha: float,
        footer: Color,
        qr_fg: str,
        pixel_rgb: tuple[int, int, int],
    ) -> None:
        self.bg = bg
        self.bg_soft = bg_soft
        self.card = card
        self.text = text
        self.muted = muted
        self.accent = accent
        self.frame_outer = frame_outer
        self.frame_inner = frame_inner
        self.blob_alpha = blob_alpha
        self.footer = footer
        self.qr_fg = qr_fg
        self.pixel_rgb = pixel_rgb


_DARK = _Palette(
    bg=HexColor("#0b0718"),
    bg_soft=HexColor("#140d29"),
    card=HexColor("#1d1440"),
    text=white,
    muted=HexColor("#94a3b8"),
    accent=_CYAN,
    frame_outer=_PINK,
    frame_inner=_VIOLET,
    blob_alpha=0.11,
    footer=Color(0.58, 0.33, 0.97, alpha=0.7),
    qr_fg="#0b0718",
    pixel_rgb=(255, 255, 255),
)

_LIGHT = _Palette(
    bg=HexColor("#f7f4ff"),
    bg_soft=HexColor("#efe8ff"),
    card=HexColor("#ffffff"),
    text=HexColor("#0b0718"),
    muted=HexColor("#64748b"),
    accent=HexColor("#0891b2"),
    frame_outer=_PINK,
    frame_inner=_VIOLET,
    blob_alpha=0.08,
    footer=Color(0.58, 0.33, 0.97, alpha=0.55),
    qr_fg="#0b0718",
    pixel_rgb=(11, 7, 24),
)


def _palette(theme: CertificateTheme) -> _Palette:
    return _LIGHT if theme == "light" else _DARK


def _register_fonts() -> tuple[str, str]:
    pairs = (
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "DejaVuSans",
            "DejaVuSans-Bold",
        ),
        (
            "/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "ArialUnicode",
            "ArialUnicode",
        ),
    )
    for regular_path, bold_path, regular_name, bold_name in pairs:
        try:
            pdfmetrics.registerFont(TTFont(regular_name, regular_path))
            pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            return regular_name, bold_name
        except Exception:
            continue
    return "Helvetica", "Helvetica-Bold"


@lru_cache(maxsize=8)
def _pil_font(size: int, *, display: bool = False) -> ImageFont.ImageFont:
    if display:
        for path in (_UNBOUNDED_EXTRABOLD, _UNBOUNDED_BOLD):
            if path.is_file():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _lerp_hex(colors: tuple[str, ...], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    stops = len(colors) - 1
    scaled = t * stops
    i = min(int(scaled), stops - 1)
    local = scaled - i
    a = tuple(int(colors[i][j : j + 2], 16) for j in (1, 3, 5))
    b = tuple(int(colors[i + 1][j : j + 2], 16) for j in (1, 3, 5))
    return tuple(int(a[k] + (b[k] - a[k]) * local) for k in range(3))  # type: ignore[return-value]


def _render_brand_wordmark(*, pixel_rgb: tuple[int, int, int]) -> ImageReader:
    font = _pil_font(96, display=True)
    pixel = "Pixel"
    gift = "gift"
    pad_x, pad_y = 12, 16

    tmp = Image.new("RGBA", (10, 10))
    measure = ImageDraw.Draw(tmp)
    pixel_bbox = measure.textbbox((0, 0), pixel, font=font)
    gift_bbox = measure.textbbox((0, 0), gift, font=font)
    pixel_w = pixel_bbox[2] - pixel_bbox[0]
    gift_w = gift_bbox[2] - gift_bbox[0]
    text_h = max(pixel_bbox[3] - pixel_bbox[1], gift_bbox[3] - gift_bbox[1])

    width = pad_x * 2 + pixel_w + gift_w
    height = text_h + pad_y * 2
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text_y = pad_y - pixel_bbox[1]
    draw.text((pad_x, text_y), pixel, font=font, fill=pixel_rgb + (255,))

    gift_x = pad_x + pixel_w
    gift_layer = Image.new("RGBA", (gift_w + 8, text_h + 16), (0, 0, 0, 0))
    gift_draw = ImageDraw.Draw(gift_layer)
    gift_draw.text((0, -gift_bbox[1]), gift, font=font, fill=(255, 255, 255, 255))
    grad = Image.new("RGBA", gift_layer.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for x in range(gift_layer.width):
        color = _lerp_hex(_GRADIENT, x / max(1, gift_layer.width - 1))
        gdraw.line([(x, 0), (x, gift_layer.height)], fill=color + (255,))
    alpha = gift_layer.split()[-1]
    colored = Image.new("RGBA", gift_layer.size, (0, 0, 0, 0))
    colored.paste(grad, (0, 0))
    colored.putalpha(alpha)
    img.paste(colored, (gift_x, pad_y - 4), colored)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


class ReportLabGiftCertificateRenderer(BaseGiftCertificateRenderer):
    def render(self, data: GiftCertificateData) -> bytes:
        font, font_bold = _register_fonts()
        pal = _palette(data.theme)
        buffer = BytesIO()
        width, height = A4
        c = canvas.Canvas(buffer, pagesize=A4)

        c.setFillColor(pal.bg)
        c.rect(0, 0, width, height, fill=1, stroke=0)

        self._blob(c, width * 0.2, height * 0.75, 90 * mm, _VIOLET, pal.blob_alpha)
        self._blob(c, width * 0.85, height * 0.3, 70 * mm, _PINK, pal.blob_alpha)
        self._blob(c, width * 0.5, height * 0.15, 50 * mm, _CYAN, pal.blob_alpha * 0.7)

        margin = 14 * mm
        c.setStrokeColor(pal.frame_outer)
        c.setLineWidth(1.8)
        c.roundRect(
            margin, margin, width - 2 * margin, height - 2 * margin, 8 * mm, fill=0, stroke=1
        )
        c.setStrokeColor(pal.frame_inner)
        c.setLineWidth(0.7)
        c.roundRect(
            margin + 3 * mm,
            margin + 3 * mm,
            width - 2 * margin - 6 * mm,
            height - 2 * margin - 6 * mm,
            6 * mm,
            fill=0,
            stroke=1,
        )

        brand = _render_brand_wordmark(pixel_rgb=pal.pixel_rgb)
        brand_w = 120 * mm
        brand_h = 26 * mm
        c.drawImage(
            brand,
            (width - brand_w) / 2,
            height - 54 * mm,
            width=brand_w,
            height=brand_h,
            mask="auto",
            preserveAspectRatio=True,
        )

        c.setFillColor(pal.muted)
        c.setFont(font, 11)
        c.drawCentredString(
            width / 2, height - 62 * mm, "Сертификат на цифровой подарок"
        )

        c.setStrokeColor(_GOLD)
        c.setLineWidth(1)
        c.line(width / 2 - 30 * mm, height - 68 * mm, width / 2 + 30 * mm, height - 68 * mm)

        c.setFillColor(pal.text)
        c.setFont(font_bold, 14)
        title = self._truncate(data.title, 48)
        c.drawCentredString(width / 2, height - 80 * mm, title)

        card_y = height - 124 * mm
        card_h = 36 * mm
        c.setFillColor(pal.card)
        if data.theme == "light":
            c.setStrokeColor(HexColor("#e9e2f8"))
            c.setLineWidth(1)
            c.roundRect(28 * mm, card_y, width - 56 * mm, card_h, 5 * mm, fill=1, stroke=1)
        else:
            c.roundRect(28 * mm, card_y, width - 56 * mm, card_h, 5 * mm, fill=1, stroke=0)

        c.setFillColor(pal.muted)
        c.setFont(font, 9)
        c.drawString(36 * mm, card_y + card_h - 12 * mm, "ДЛЯ")
        c.setFillColor(pal.text)
        c.setFont(font_bold, 16)
        c.drawString(36 * mm, card_y + card_h - 22 * mm, data.recipient_name)

        c.setFillColor(pal.muted)
        c.setFont(font, 9)
        c.drawString(36 * mm, card_y + 10 * mm, "ОТКРОЕТСЯ")
        c.setFillColor(pal.accent)
        c.setFont(font, 11)
        c.drawString(36 * mm, card_y + 4 * mm, data.activates_at_label)

        pwd_y = card_y - 32 * mm
        c.setFillColor(pal.bg_soft)
        c.setStrokeColor(_GOLD)
        c.setLineWidth(1)
        c.roundRect(28 * mm, pwd_y, width - 56 * mm, 24 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(_GOLD if data.theme == "dark" else HexColor("#b45309"))
        c.setFont(font, 9)
        c.drawCentredString(width / 2, pwd_y + 15 * mm, "ПАРОЛЬ ДЛЯ ОТКРЫТИЯ")
        c.setFillColor(pal.text)
        c.setFont(font_bold, 18)
        c.drawCentredString(width / 2, pwd_y + 5 * mm, data.unlock_password)

        qr_img = self._qr_image(data.gift_url, fg=pal.qr_fg)
        qr_size = 55 * mm
        qr_x = (width - qr_size) / 2
        qr_y = pwd_y - 68 * mm
        c.setFillColor(white)
        c.setStrokeColor(HexColor("#e2e8f0") if data.theme == "light" else HexColor("#1d1440"))
        c.setLineWidth(0.5)
        c.roundRect(
            qr_x - 4 * mm,
            qr_y - 4 * mm,
            qr_size + 8 * mm,
            qr_size + 8 * mm,
            3 * mm,
            fill=1,
            stroke=1,
        )
        c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size, mask="auto")

        c.setFillColor(pal.muted)
        c.setFont(font, 9)
        c.drawCentredString(
            width / 2, qr_y - 10 * mm, "Отсканируй QR — откроется страница подарка"
        )

        c.setFillColor(pal.accent)
        c.setFont(font, 8)
        url_label = self._truncate(data.gift_url, 64)
        c.drawCentredString(width / 2, qr_y - 16 * mm, url_label)

        if data.message:
            c.setFillColor(pal.muted)
            c.setFont(font, 9)
            msg = self._truncate(data.message.replace("\n", " "), 80)
            c.drawCentredString(width / 2, margin + 18 * mm, f"«{msg}»")

        c.setFillColor(pal.footer)
        c.setFont(font, 8)
        c.drawCentredString(width / 2, margin + 8 * mm, "pixelgift")

        c.showPage()
        c.save()
        return buffer.getvalue()

    @staticmethod
    def _blob(
        c: canvas.Canvas,
        x: float,
        y: float,
        radius: float,
        color: HexColor,
        alpha: float,
    ) -> None:
        c.saveState()
        c.setFillColor(Color(color.red, color.green, color.blue, alpha=alpha))
        c.circle(x, y, radius, fill=1, stroke=0)
        c.restoreState()

    @staticmethod
    def _qr_image(url: str, *, fg: str = "#0b0718") -> ImageReader:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fg, back_color="white").convert("RGB")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return ImageReader(buf)

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        text = text.strip()
        if len(text) <= max_len:
            return text
        return text[: max_len - 1].rstrip() + "…"
