from PIL import Image

from src.logger import logger


class PdfGenerator:

    def generate_pdf(
        self,
        image_file,
        pdf_file
    ):

        image = Image.open(
            image_file
        )

        image = image.convert(
            "RGB"
        )

        image.save(
            pdf_file,
            "PDF"
        )

        logger.info(
            f"✅ PDF generado: {pdf_file}"
        )