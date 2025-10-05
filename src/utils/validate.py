from handlers.base import Errors

try:
    import ddddocr
except Exception:
    ddddocr = None
    pass

if ddddocr is not None:
    OCR = ddddocr.DdddOcr()


def get_validate_code(img_bytes: bytes) -> str | Errors:
    if ddddocr is not None:
        return OCR.classification(img_bytes).lower()
    return Errors.MissingDDDDOCR
