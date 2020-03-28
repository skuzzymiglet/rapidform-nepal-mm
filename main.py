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

def scan():
    pass
def parse():
    pass

def main():
    imageToTransform = "/src/tests/assets/nepal2.jpg"
    outFilename = "/src/out/aligned_nepal2.jpg"
    textDetctionResultJson = "tests/assets/nepal2_text_detection.json"
    saveAlignedImage(
        imageToTransform, outFilename, textDetctionResultJson
    )

if __name__ == "__main__":
    main()