import ddddocr

OCR = ddddocr.DdddOcr()


def get_validate_code(img_bytes: bytes):
    return OCR.classification(img_bytes).lower()
