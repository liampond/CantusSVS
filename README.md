# CantusSVS

CantusSVS is a singing voice synthesis tool that automatically generates audio playback for the Latin chants in Cantus. We use **DiffSinger**, a diffusion-based singing voice synthesis model described in the paper below:

**DiffSinger: Singing Voice Synthesis via Shallow Diffusion Mechanism**  

Liu, Jinglin, Chengxi Li, Yi Ren, Feiyang Chen, and Zhou Zhao. 2022. "Diffsinger: Singing Voice Synthesis via Shallow Diffusion Mechanism." In *Proceedings of the AAAI Conference on Artificial Intelligence* 36 10: 11020–11028. [https://arxiv.org/abs/2105.02446](http://dx.doi.org/10.1609/aaai.v36i10.21350).

The training procedure follows the guidelines detailed in [this tutorial](https://docs.google.com/document/d/1uMsepxbdUW65PfIWL1pt2OM6ZKa5ybTTJOpZ733Ht6s/view) by [PixPrucer](https://bsky.app/profile/pixprucer.bsky.social). For help, join the [DiffSinger Discord server](https://discord.gg/DZ6fhEUfnb).

The model was trained using this [Google Colab notebook](https://github.com/usamireko/DiffSinger_colab_notebook_MLo7) created by [Ghin_MLo7](https://github.com/MLo7Ghinsan) and [Sumireko Usami](https://github.com/usamireko).

---

## OpenUtau

Music is rendered using [OpenUtau](https://github.com/stakira/openutau/releases) version **0.1.547 (beta)**. In the future, macros will be used to automate this process. If you encounter difficulties with OpenUtau, look through these pages:
  - [Getting Started Tutorial](https://github.com/stakira/OpenUtau/wiki/Getting-Started)  
  - [FAQ](https://github.com/stakira/OpenUtau/wiki/FAQ)
