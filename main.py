import streamlit as st
import torch, torchvision
# import req
import numpy as np
import os, json, random, cv2
from detectron2 import model_zoo
from detectron2.utils.logger import setup_logger
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.data.catalog import Metadata
from PIL import Image, ImageOps
''''''
import time

page_bg_img = """
<style>
[data-testid="stAppViewContainer"]  {
background-image: url("https://static-cse.canva.com/blob/573141/RainbowGradientPinkandPurpleZoomVirtualBackground.jpg");
background-size: cover;
background-position: top left;
background-repeat: no-repeat;
}
[data-testid="stHeader"] {
background: rgba(0,0,0,0);
background-image: url("https://zaka.ai/wp-content/uploads/2022/03/logo-black.png");
background-size: 10%;
background-repeat: no-repeat;
margin-top: 20px;
left: 0.2cm;
}
[data-testid="stDecoration"] {
position: absolute;
    top: -100px;
    right: 0px;
    left: 0px;
    height: 0.125rem;
    z-index: 999990;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


@st.cache(persist=True)
def initialization():
    """Loads configuration and model for the prediction.

    Returns:
        cfg (detectron2.config.config.CfgNode): Configuration for the model.
        predictor (detectron2.engine.defaults.DefaultPredicto): Model to use.
            by the model.

    """
    # Import some common detectron2 utilities
    NUM_CLASSES = 7
    # Then, we create a detectron2 config and a detectron2 `DefaultPredictor` to run inference on this image.
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cpu"
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = slider
      # set threshold for this model
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = NUM_CLASSES
    # Custom Trained Model
    cfg.MODEL.WEIGHTS = os.path.join("model_final.pth")
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512  # 128

    # minimum image size for the train set
    cfg.INPUT.MIN_SIZE_TRAIN = (800,)
    # maximum image size for the train set
    cfg.INPUT.MAX_SIZE_TRAIN = 1333
    # minimum image size for the test set
    cfg.INPUT.MIN_SIZE_TEST = 800
    # maximum image size for the test set
    cfg.INPUT.MAX_SIZE_TEST = 1333

    # Predictor
    predictor = DefaultPredictor(cfg)

    return cfg, predictor


@st.cache
def inference(predictor, img):
    return predictor(img)

@st.cache
def output_image(img_array, outputs):
    v = Visualizer(img_array[:, :, ::-1], metadata=my_metadata, instance_mode=ColorMode.IMAGE_BW,
                   # removes the colors of unsegmented pixels
                   scale=1.2)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    processed_img = out.get_image()[:, :, ::-1]

    return processed_img

# Detectron2 Setup Logger
setup_logger()


# Detectron2 Metadata
my_metadata = Metadata()
my_metadata.set(thing_classes=['metals_and_plastics', 'other', 'non-recyclable', 'glass', 'paper', 'bio', 'unknown'])
cats = ['metals_and_plastics', 'other', 'non-recyclable', 'glass', 'paper', 'bio', 'unknown']

# Streamlit Title
st.title('Waste Detector:')
st.caption('Using Detectron2 (BBox+Segmentation)')

st.write('\n')

# st.write('Test image')
# im = cv2.imread("assets/test.JPG")
# # showing image
# st.image('assets/test.JPG')



###
# Upload images
slider = st.slider('Choose Threshold for the Detection', min_value=0.0, max_value=1.0, value=0.4, step=0.1)
st.write('Upload image')
upload = st.file_uploader("Please upload an image", type=["jpg","png", "jpeg", "heif"])
if upload is not None:
    st.write('Image Uploaded:')
    image = Image.open(upload).convert('RGB')
    st.image(image, use_column_width=True)
    img_array = np.array(image)
    cfg, predictor = initialization()

    outputs = predictor(img_array)

    st.title('Prediction Outputs:')
    st.write('Pred Classes: ',outputs["instances"].pred_classes)
    st.write('Categories: ',cats)
    # st.write('Pred Boxes: ',outputs["instances"].pred_boxes)
    st.write('Scores: ', outputs["instances"].scores)

    st.write('Using Vizualizer to draw the predictions on Image')

    out_image = output_image(img_array, outputs)
    st.image(out_image, caption='Processed Image', use_column_width=True)

''''''
