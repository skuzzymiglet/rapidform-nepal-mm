import cv2
import json 
import matplotlib.pyplot as plt
import numpy as np

MAX_FEATURES = 22
GOOD_MATCH_PERCENT = 0.99
REFERENCE_FORM_IMAGE_PATH= "/src/assets/form_template.jpg"
REFERENCE_FORM_TEXT_DETECTION_JSON_PATH = "/src/assets/form_template_text_detection.json"

ANCHOR_TEXT = [
    "Contact", "Health", "Government", "To", "www.facebook.com/edcdnepal"
    # "Government", "To", "From", "Health", "5.9"
]

def featuresForImage(jsonFilepath):
    with open(jsonFilepath) as f:
        data = json.load(f)
        return [ coordinatesForText(text, data) for text in ANCHOR_TEXT ]

def coordinatesForText(text, json):
    annotations = json["responses"][0]["textAnnotations"]
    for annotation in annotations:
        if "description" in annotation and annotation["description"].startswith(text):
            coordinate = annotation["boundingPoly"]["vertices"][0]
            return [coordinate["x"], coordinate["y"]]

    raise Exception("'%s' not found" % text)

WORD_TO_IGNORE = "Nose" # HACK! so "No" doesn't match to "Nose"
def allCoordinatesForText(text, json, matchOnPrefix=False): #matchOnPrefix is necessary because the vision API finds text like "NoD", which really is "No"
    annotations = json["responses"][0]["textAnnotations"]
    coordinates = []
    
    for annotation in annotations:
        if "description" in annotation:
            if annotation["description"].startswith(WORD_TO_IGNORE):
                continue    

            matches = annotation["description"].startswith(text) if matchOnPrefix else annotation["description"] == text
            if matches:
                coordinate = annotation["boundingPoly"]["vertices"][0]
                coordinates.append((coordinate["x"], coordinate["y"]))
    
    return coordinates


def alignImages(im1, im2, im1TextDetectionJsonPath, im2TextDetectionJsonPath):
    keypoints1 = featuresForImage(im1TextDetectionJsonPath)
    keypoints2 = featuresForImage(im2TextDetectionJsonPath)

    # Extract location of good matches
    points1 = np.zeros((len(ANCHOR_TEXT), 2), dtype=np.float32)
    points2 = np.zeros((len(ANCHOR_TEXT), 2), dtype=np.float32)

    for i in range(0, len(ANCHOR_TEXT)):
        points1[i, :] = keypoints1[i]
        points2[i, :] = keypoints2[i]

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width, channels = im2.shape
    im1Reg = cv2.warpPerspective(im1, h, (width, height))
  
    return im1Reg, h

def saveAlignedImage(imFilename, outFilename, textDetctionResultJsonPath):
    # Read reference image
    print("Reading reference image : ", REFERENCE_FORM_IMAGE_PATH)
    imReference = cv2.imread(REFERENCE_FORM_IMAGE_PATH, cv2.IMREAD_COLOR)

    # Read image to be aligned
    print("Reading image to align : ", imFilename)
    im = cv2.imread(imFilename, cv2.IMREAD_COLOR)

    print("Aligning images ...")
    # Registered image will be resotred in imReg. 
    # The estimated homography will be stored in h. 
    imReg, h = alignImages(im, imReference, textDetctionResultJsonPath, REFERENCE_FORM_TEXT_DETECTION_JSON_PATH)

    # Write aligned image to disk. 
    print("Saving aligned image : ", outFilename)
    writeResult = cv2.imwrite(outFilename, imReg)
    print("write result: ", writeResult)

    # Print estimated homography
    print("Estimated homography : \n",  h)

CHECKBOX_LABELS = {
    "Male": { "count": 1, "width": 47, "height": 23 },
    "Female": { "count": 1, "width": 68, "height": 23 },
    "Others": { "count": 1, "width": 61, "height": 23 },
    "Yes": { "count": 13, "width": 38, "height": 22 },
    "No": { "count": 11, "width": 27, "height": 22 },  # TODO this count should be 13, but Google vision isn't picking up the last 2. Maybe we can ignore finding "No" and just use offsets off of the "Yes" coordinates
}

GENDER_OPTIONS = ["Male", "Female", "Others"]

def extractCheckboxes(alignedImageTextDetectionJsonPath):
    with open(alignedImageTextDetectionJsonPath) as f:
        checkboxTopLeftCoordinates = {}
        data = json.load(f)
        result = []
        for label, labelDetails in CHECKBOX_LABELS.items():
            coordinatesFound = allCoordinatesForText(label, data, True)
            expectedCount = labelDetails["count"]
            if len(coordinatesFound) != expectedCount:

                # This is getting raised because the vision API is only finding 11 "No" labels.
                raise Exception("Found %s instances of '%s' != %s expected) in %s" % (len(coordinatesFound), label, expectedCount, alignedImageTextDetectionJsonPath))
            checkboxTopLeftCoordinates[label] = [ (c[0] + labelDetails["width"], c[1]) for c in coordinatesFound ]
            
        return checkboxTopLeftCoordinates

CHECKBOX_CROP_WIDTH = 23
CHECKBOX_CROP_HEIGHT = 21

def compareCheckboxes(labelToCheckboxLoc, image):
    for label, loc in labelToCheckboxLoc.items():
        box = image[loc[0]:loc[0]+CHECKBOX_CROP_HEIGHT, loc[1]:loc[1]+CHECKBOX_CROP_WIDTH]
        
        # TODO determine which box has the most gray to determine which checkbox is checked
        writeResult = cv2.imwrite("/src/out/"+label+".jpg", box) # Use this output to make sure we're looking at a checkbox

    return None


# TODO parameterize this with an image
# And make this actually call the vision API
def main():
    imageToTransformPath = "/src/tests/assets/nepal2.jpg"
    alignedImagePath = "/src/out/aligned_nepal2.jpg"
    textDetctionResultJsonPath = "/src/tests/assets/nepal2_text_detection.json"
    saveAlignedImage(
        imageToTransformPath, alignedImagePath, textDetctionResultJsonPath
    )

    alignedImageTextDetectionResultJsonPath = "/src/tests/assets/aligned_nepal2_text_detection.json"
    checkboxLocations = extractCheckboxes(alignedImageTextDetectionResultJsonPath)
    
    image = cv2.imread(alignedImagePath)
    genderToCheckbox = dict([ [label, checkboxLocations[label][0]] for label in GENDER_OPTIONS ])
    print(genderToCheckbox)
    gender = compareCheckboxes(genderToCheckbox, image)
    
    print(gender)

    # TODO process checkboxes for Yes/No questions after getting the last 2 coordinates for "No" (the google vision API finds 11)
    # orderedYesLocations = sorted(checkboxLocations["Yes"], key=lambda loc: loc[1])
    # orderedNoLocations = sorted(checkboxLocations["No"], key=lambda loc: loc[1])
    # yesNoResults = []
    # for i in range(len(orderedYesLocations)):
    #     res = compareCheckboxes({ "Yes": orderedYesLocations[i], "No": orderedNoLocations[i] }, image)
    #     yesNoResults += [res]
    

if __name__ == "__main__":
    main()