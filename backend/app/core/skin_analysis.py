import time
import json
from app.core.logger import logger

def run_mock_skin_analysis(image_path: str) -> dict:
    """
    Mock function to simulate a long-running skin analysis (e.g. AI model inference).
    This is designed to be modular. Your colleague can replace the contents of this 
    function with the actual AI logic from Tesis 1.0.
    
    Args:
        image_path: The path to the image to analyze.
        
    Returns:
        dict: A dictionary containing the analysis results.
    """
    logger.info(f"Starting mock skin analysis for image: {image_path}")
    
    # Simulate processing time (e.g., loading model, running inference)
    time.sleep(10)
    
    # Simulated result structure
    mock_result = {
        "skin_type": "mixta",
        "concerns": ["acne", "poros dilatados"],
        "recommended_ingredients": ["salicylic_acid", "niacinamide"],
        "fitzpatrick": "III"
    }
    
    logger.info("Mock skin analysis completed")
    return mock_result
