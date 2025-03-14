# CantusSVS

CantusSVS is a singing voice synthesis tool that automatically generates audio playback for the Latin chants in Cantus. We use **DiffSinger**, a diffusion-based singing voice synthesis model described in the paper below:

**DiffSinger: Singing Voice Synthesis via Shallow Diffusion Mechanism**  

Liu, Jinglin, Chengxi Li, Yi Ren, Feiyang Chen, and Zhou Zhao. 2022. "Diffsinger: Singing Voice Synthesis via Shallow Diffusion Mechanism." In *Proceedings of the AAAI Conference on Artificial Intelligence* 36 (10): 11020–11028. [https://doi.org/10.1609/aaai.v36i10.21350](https://doi.org/10.1609/aaai.v36i10.21350).

The dataset creation procedure follows the guidelines detailed in [this tutorial](https://docs.google.com/document/d/1uMsepxbdUW65PfIWL1pt2OM6ZKa5ybTTJOpZ733Ht6s/view) by [PixPrucer](https://bsky.app/profile/pixprucer.bsky.social). For help, join the [DiffSinger Discord server](https://discord.gg/DZ6fhEUfnb).

Training was performed using GPUs provided by the Digital Research Alliance of Canada (DRAC). If you are a DDMAL member, find out how to gain access to DRAC on [this page](https://wiki.internal.simssa.ca/wiki/Digital_Research_Alliance_of_Canada). Otherwise, for help using DRAC, follow these tutorials:
-[Getting Started](https://docs.alliancecan.ca/wiki/Getting_started)
-[Machine Learning Tutorial](https://docs.alliancecan.ca/wiki/Tutoriel_Apprentissage_machine/en)
-[Python Package Installation](https://docs.alliancecan.ca/wiki/Python#Creating_and_using_a_virtual_environment)

To train locally, follow [this tutorial](https://www.youtube.com/watch?v=Sxt11TAflV0) by [tigermeat](https://www.youtube.com/@spicytigermeat).

The model can also be trained using this [Google Colab notebook](https://github.com/usamireko/DiffSinger_colab_notebook_MLo7) created by [Ghin_MLo7](https://github.com/MLo7Ghinsan) and [Sumireko Usami](https://github.com/usamireko).
