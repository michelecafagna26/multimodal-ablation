# VL-Ablation
*Official implementation of the **multimodal input ablation method** used in the paper: ["What Vision-Language Models 'See' when they See Scenes"](https://arxiv.org/abs/2109.07301).*

---
A tool to perform targeted semantic multimodal input ablation. It allows to perform textual ablation based on noun-phrases instead of tokens, and visual ablation based on the content of a text.

### Overview

- **🗃️ Repository:** [github.com/michelecafagna26/vl-ablation](https://github.com/michelecafagna26/vl-ablation)
- **📜 Paper:** [What Vision-Language Models 'See' when they See Scenes](https://arxiv.org/abs/2109.07301)
- **🖊️ Contact:** michele.cafagna@um.edu.mt

### Requirements

```txt
python >3.8
pytorch
torchvision
```

### Installation

```bash
pip install git+https://github.com/michelecafagna26/vl-ablation.git#egg=ablation
```

# Download the models
If you haven't done already download the spacy model specified in the ```config.json```, by running
```bash
python3 -m spacy download en_core_web_md
```
Download the Fasttext model in the ```ablation/data``` folder

```bash
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz -P ablation/data
tar -xf ablation/data/cc.en.300.bin.gz
```

# Quick Start
```python3
```

### Citation Information

```BibTeX
@article{cafagna2021vision,
  title={What Vision-Language ModelsSee'when they See Scenes},
  author={Cafagna, Michele and van Deemter, Kees and Gatt, Albert},
  journal={arXiv preprint arXiv:2109.07301},
  year={2021}
}
```
