from io import BytesIO
import qrcode


def generate_qr_png_bytes(data: str, box_size: int = 10, border: int = 4) -> bytes:
    """Generate a QR code PNG as bytes for the provided data."""
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
