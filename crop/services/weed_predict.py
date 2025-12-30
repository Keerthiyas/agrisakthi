def detect_weed(image):
    """
    Quick demo: Detect weed based on the file name.
    If file name contains 'nutgrass', return Nutgrass.
    Otherwise, default to Crabgrass.
    """
    filename = image.name.lower()  # get the uploaded file name in lowercase

    if "nutgrass" in filename:
        return "Nutgrass", 90.0  # high confidence for demo
    elif "barnyard" in filename:
        return "Barnyard Grass", 85.0
    else:
        return "Crabgrass", 50.0  # default
