import cv2
import spacy
import numpy as np
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import ToTensor

from annoy import AnnoyIndex
from gensim.models.fasttext import load_facebook_model
import compress_fasttext

from ablation.util import load_config, get_logger

COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]


class VisualAblator():

    def __init__(self, fasttext_model_path=None, device="cpu", distilled=True):

        self.logger = get_logger(__name__)
        self.config = load_config()
        # Creating an object
        self.device = device
        self.detector = fasterrcnn_resnet50_fpn(pretrained=True).to(self.device)
        self.logger.info("Object Detector Loaded")

        self.nlp = spacy.load(self.config['spacy_model'])
        
        if distilled:
        
            # Loading the index
            self.u = AnnoyIndex(300, 'angular')
            self.u.load(self.config['coco_classes_index_distil'])  # super fast, it will just mmap the file
            self.logger.info("COCO classes distilled index loaded")

            # Loading Compressed Fasttext's model
            self.logger.warning("Loading distilled Fasttext model. It shouldn't take long...")
            self.wv = compress_fasttext.models.CompressedFastTextKeyedVectors.load(self.config['fasttext_model_distil'])
            self.logger.info("Distilled Fasttext Model loaded")

        else:

            if not fasttext_model_path:
                self.logger.info("If you're not using the distilled model, 'fasttext_model_path' needs to be specified.")
                raise ValueError("If you're not using the distilled model, 'fasttext_model_path' needs to be specified.")

            # Loading the index
            self.u = AnnoyIndex(300, 'angular')
            self.u.load(self.config['coco_classes_index'])  # super fast, it will just mmap the file
            self.logger.info("COCO classes index loaded")

            # Loading Fasttext's model
            self.logger.warning('Loading Fasttext model, this may take a while...')
            self.wv = load_facebook_model(fasttext_model_path).wv
            self.logger.info("Fasttext Model loaded")

    # Extract bounding boxes
    def get_detections(self, image):

        image = ToTensor()(image).unsqueeze(0).to(self.device)

        self.detector.eval()
        preds = self.detector(image)[0]

        return {
            "boxes": preds['boxes'].cpu().detach().numpy(),
            "labels": preds['labels'].cpu().numpy().tolist(),
            "scores": preds['scores'].cpu().detach().numpy().tolist()
        }

    """
    Find COCO classes mentioned in the caption
    """
    def extract_candidates(self, caption, th=0.98):

        doc = self.nlp(caption, disable=['tok2vec', 'parser', 'senter', 'ner'])
        tokens_lemmas = [token.lemma_ for token in doc]
        candidates = []


        # extract the best candidates
        for i in range(len(tokens_lemmas)):
            s = self.u.get_nns_by_vector(self.wv[tokens_lemmas[i]], n=1, include_distances=True)

            if s[1][0] <= th:
                candidates.append({
                    "token": tokens_lemmas[i],
                    "confidence": s[1][0],
                    "coco_class": COCO_INSTANCE_CATEGORY_NAMES[s[0][0]],
                    "coco_idx": s[0][0]
                })

        return candidates

    def patch_image(self, img, preds: dict, coco_candidates: list, detection_th=0.9):

        grey = (0.5, 0.5, 0.5)
        img = np.dstack(ToTensor()(img).cpu().numpy().squeeze())

        ablated_boxes = []
        for i, box in enumerate(preds['boxes']):
            for coco_c in coco_candidates:
                if COCO_INSTANCE_CATEGORY_NAMES[preds['labels'][i]] == coco_c['coco_class'] and preds['scores'][i] >= detection_th:
                    cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), grey, -1)

                    ablated_boxes.append({
                        "box": box,
                        "score": preds['scores'][i],
                        "coco_class": COCO_INSTANCE_CATEGORY_NAMES[preds['labels'][i]],
                        "coco_idx": preds['labels'][i],
                        "token": coco_c['token']
                    })

        # covert from np.array(float32) to np.array(unit8)
        img = (img * 255 / np.max(img)).astype('uint8')
        # return a PIL image
        return Image.fromarray(img), ablated_boxes

    def __call__(self, img, caption, detection_th=0.9):

        coco_candidates = self.extract_candidates(caption)
        preds = self.get_detections(img)
        img = np.dstack(ToTensor()(img).cpu().numpy().squeeze())

        return self.patch_image(img, preds, coco_candidates, detection_th)