import pytesseract
from PIL import Image, ImageFilter, ImageOps
from io import BytesIO

def solve_captcha(browser, captcha_element):
    """
    Captures and solves CAPTCHA from the given browser and CAPTCHA element.
    Returns the cleaned CAPTCHA text.
    """
    try:
        # Get CAPTCHA image as PNG from the element
        captcha_png = captcha_element.screenshot_as_png
        image = Image.open(BytesIO(captcha_png))

        # Optional: save original for debugging
        image.save("captcha_original.png")

        # --- Image preprocessing ---
        image = image.convert("L")  # Convert to grayscale
        image = ImageOps.invert(image)  # Invert for better OCR contrast (if background is dark)
        image = image.point(lambda x: 0 if x < 140 else 255, '1')  # Binarize
        image = image.filter(ImageFilter.MedianFilter())  # Reduce noise

        # Optional: save processed image for debugging
        image.save("captcha_processed.png")

        # --- OCR with improved config ---
        custom_config = r'--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        captcha_text = pytesseract.image_to_string(image, config=custom_config)

        # Clean up text
        captcha_text = captcha_text.strip().replace(" ", "").replace("\n", "")

        return captcha_text
    except Exception as e:
        print(f"Captcha solving error: {e}")
        return ""
