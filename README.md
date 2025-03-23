# Image Analysis Repository
This Repository contains scripts and instructions for several image analysis workflows. This README file contains an overview of the different workflows and tools. More detailed information can be found in the subdirectories and the linked publications. All README files are supplied in Markdown and PDF formt

## 1. Single Cells
This folder contains two workflows for single cell analysis. The older one uses Ilastik for the segmentation and FIJI/ImageJ for further analysis. The newer workflow mostly uses DeLTA and also includes the tracking of single cells over time.

__related publications:__
[Space and genealogy determine inter-individual differences in siderophore gene expression in bacterial colonies](https://www.cell.com/cell-reports/fulltext/S2211-1247(24)00434-0)

[Single-Cell Imaging Reveals That _Staphylococcus aureus_ Is Highly Competitive Against _Pseudomonas aeruginosa_ on Surfaces](https://www.frontiersin.org/articles/10.3389/fcimb.2021.733991/full?field=&id=733991&journalName=Frontiers_in_Cellular_and_Infection_Microbiology)

## 2. Microcolonies 
This workflow can be used to follow micro-colonies growing on agarose pads. It segments the micro-colonies as a whole, tracks them over time, and provides tools to correct the segmentation and tracking. 

__related publications:__
[Interactions between _Pseudomonas aeruginosa_ and six opportunistic pathogens cover a broad spectrum from mutualism to antagonism](https://www.biorxiv.org/content/10.1101/2024.03.22.586229v1)

## 3. Colonies
This workflow can be used to analyse colonies (mixed or mono) growing on plates. It consists or one ImageJ script that converts '.lif' files to individual TIFF images and measures the fluorescence within a colony or over the whole field of view, depending on what option is selected.

## 4. Zebrafish
This workflow is used to segment the otic vesical of Zebrafish and measure the state of co infections within it, based on fluorescence.

__related publications:__
[A new protocol for multispecies bacterial infections in zebrafish and their monitoring through automated image analysis](https://www.biorxiv.org/content/10.1101/2024.01.15.575759v2)

## 5. Tools
This folder contains scripts that are used in different workflows and can be useful when working with microscopy data. 