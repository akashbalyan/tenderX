import sys
import os

# Add the 'backend' folder to the sys.path to allow imports from the scraper subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'scraper')))

from tender_scraper import main_function  # Replace with your main function

if __name__ == "__main__":
    main_function()