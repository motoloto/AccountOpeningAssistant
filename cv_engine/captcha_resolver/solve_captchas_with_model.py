import cv2
import pytesseract


class ImageReader:
    # def __init__(self):
        # self.MODEL_FILENAME = "Captcha_resolver/captcha_model.hdf5"
        # self.MODEL_LABELS_FILENAME = "Captcha_resolver/model_labels.dat"
        # CAPTCHA_IMAGE_FOLDER = "generated_captcha_images"

        # Load up the model labels (so we can translate model predictions to actual letters)
        # self.lb = None
        # with open(self.MODEL_LABELS_FILENAME, "rb") as f:
        #     self.lb = pickle.load(f)

        # Load the trained neural network
        # self.model = load_model(self.MODEL_FILENAME)

    def solve_captcha(self, image_file):

        # Load the image and convert it to grayscale
        image = cv2.imread(image_file)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image2 = cv2.copyMakeBorder(image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[225,225,225])
        thresh = cv2.threshold(image2, 0, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)[1]

        predictions = pytesseract.image_to_data(thresh, lang='eng', config='-psm 7', output_type="dict")

        conf = predictions.get('conf')[-1]
        text = predictions.get('text')[-1]

        result = {
            'conf': conf,
            'text': text
        }
        print('OCR result:' + str( result))
        # Show the annotated image
        # cv2.imshow("Output", output)
        # cv2.waitKey()
        return result

    def solve_multi_captcha(self, captcha_folder):

        # Grab some random CAPTCHA images to test against.
        # In the real world, you'd replace this section with code to grab a real
        # CAPTCHA image from a live website.
        captcha_image_files = list(captcha_folder)

        # loop over the image paths
        for image_file in captcha_image_files:
            self.solve_captcha(image_file)
