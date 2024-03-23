# VL-Ablation
*Official implementation of the **multimodal input ablation method** introduced in the paper: ["What Vision-Language Models 'See' when they See Scenes"](https://arxiv.org/abs/2109.07301).*

---
A tool to perform targeted semantic multimodal input ablation. It allows to perform textual ablation based on noun-phrases instead of tokens, and visual ablation based on the content of a text.

## Overview

- **🗃️ Repository:** [github.com/michelecafagna26/vl-ablation](https://github.com/michelecafagna26/vl-ablation)
- **📜 Paper:** [What Vision-Language Models 'See' when they See Scenes](https://arxiv.org/abs/2109.07301)
- **🖊️ Contact:** michele.cafagna@um.edu.mt

## Requirements

```txt
python=>3.8
pytorch
torchvision
```

## Installation

Install dependecies
```bash
pip install git+https://github.com/michelecafagna26/compress-fasttext
```

install the vl-ablation

```bash
pip install git+https://github.com/michelecafagna26/vl-ablation.git#egg=ablation
```

## Download the models
Download the Spacy model

```bash
python3 -m spacy download en_core_web_md
```

### [Optional]
If you want to use the full model, download the original not-distilled Fasttext model 
```bash
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz
gzip -d cc.en.300.bin.gz
```

## Quick Start
### Textual Ablation

```python3
from ablation.textual import TextualAblator

t_ablator = TextualAblator()
caption = "A table with pies being made and a person standing near a wall with pots and pans hanging on the wall"
ablations = t_ablator(caption)
```
```ablations``` is a list of ablations looking like this:
```
[{'nps': (A table,),
  'nps_index': [0],
  'ablated_caption': 'pies being made and a person standing near a wall with pots and pans hanging on the wall'},
 {'nps': (pies,),
  'nps_index': [1],
  'ablated_caption': 'A table and a person standing near a wall with pots and pans hanging on the wall'},
 ...]

```
where ```nps``` is the noun phrase ablated, ```nps_index``` is the noun phrase index and ```ablated_caption``` is the caption without the ablated noun phrases.
The list contains all the possible combinations of noun phrases in the text.

### Visual Ablation
```python3
from ablation.visual import VisualAblator
from PIL import Image
from io import BytesIO
import requests

img_url = "http://farm6.staticflickr.com/5003/5318500980_18b4dcf1fd_z.jpg"

# load the image
response = requests.get(img_url)
img = Image.open(BytesIO(response.content))

# perform visual ablation based on the text content
v_ablator = VisualAblator()
ablated_img, boxes = v_ablator(img, "a man in front of a stop sign")
```

The ablator **identifies objects mentioned in the caption that are also present in the image**. **The match is performed semantically**, thus no exact match between the object label and the text is required.

```ablated_img``` is the result of the ablation, namely the image with grey patches applied in correspondence of the objects identified as bounding boxes

```boxes``` looks like this:
```
[{'token': 'man',
  'confidence': 0.7822560667991638,
  'coco_class': 'person',
  'coco_idx': 1}]
```
Note that the ablator can identify only the set of objects present in the COCO annotations.
**Check the notebook [demo](https://github.com/michelecafagna26/vl-ablation/blob/main/demo.ipynb) to run this code.**

## Use the full Fasttest model

If you want to use full model initialize the ablatori as follows:

```python
fasttext_model = "path/to/the/model"

v_ablator = VisualAblator(fasttext_model, distilled=False)
```

## Hardware requirements

If you use the distilled model (enabled by default) the fasttext model will take less then 5GB.

Be aware that the original not-distilled fasttext embeddings takes around 13-14 GB in memory.

## Citation Information

```BibTeX
@article{cafagna2021vision,
  title={What Vision-Language ModelsSee'when they See Scenes},
  author={Cafagna, Michele and van Deemter, Kees and Gatt, Albert},
  journal={arXiv preprint arXiv:2109.07301},
  year={2021}
}
```
