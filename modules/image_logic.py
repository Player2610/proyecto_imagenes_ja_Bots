import io
import re
import unicodedata
import zipfile


try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


# Optional: enables AVIF support if installed (pillow-avif-plugin)
try:  # pragma: no cover
    import pillow_avif  # type: ignore # noqa: F401
except Exception:  # pragma: no cover
    pillow_avif = None


def safe_zip_folder_name(name: str) -> str:
    name = (name or "producto").strip()
    for ch in ("/", "\\", ":", "*", "?", '"', "<", ">", "|"):
        name = name.replace(ch, "-")
    name = " ".join(name.split())
    return name[:120] or "producto"


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "producto"


def new_image_name(product_name: str, idx: int, ext: str = ".jpg") -> str:
    base = slugify(product_name)
    if idx <= 1:
        return f"{base}{ext}"
    return f"{base}-{idx}{ext}"


def convert_bytes_to_jpg(image_bytes: bytes, quality: int = 92) -> tuple[bytes, int, int]:
    """Convert any supported image bytes to JPG, preserving resolution/aspect."""
    if Image is None:
        raise RuntimeError("PIL no disponible; no puedo convertir a JPG")

    with Image.open(io.BytesIO(image_bytes)) as im:
        im.load()
        w, h = im.size

        if im.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            alpha = im.split()[-1]
            bg.paste(im.convert("RGB"), mask=alpha)
            im = bg
        else:
            im = im.convert("RGB")

        out = io.BytesIO()
        im.save(out, format="JPEG", quality=int(quality), optimize=True)
        return out.getvalue(), int(w), int(h)


def is_low_resolution(w: int, h: int, min_px: int = 500) -> bool:
    return int(w) < int(min_px) or int(h) < int(min_px)


def build_images_zip(product_name: str, images: list[tuple[str, bytes]]) -> bytes:
    """Builds a zip containing a single folder with JPG images.

    images: list of (original_name, bytes)
    """
    zip_root = safe_zip_folder_name(product_name)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        names = []
        for idx, (_orig_name, raw) in enumerate(images, 1):
            out_name = new_image_name(product_name, idx, ext=".jpg")
            jpg_bytes, _w, _h = convert_bytes_to_jpg(raw)
            zf.writestr(f"{zip_root}/{out_name}", jpg_bytes)
            names.append(out_name)

        zf.writestr(f"{zip_root}/manifest.txt", "\n".join(names))

    return buf.getvalue()
