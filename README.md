# Steganography_F5

## Devloping a website for our pfe project
### Front end:
we used HTML,CSS,JavaScript
### Backend:
we used Flask-python

## Steganography F5 algorithme:

### What is Steganography?
Steganography is the art of hiding a secret message within (or even on top of) a non-secret object. This can be anything you want. Many forms of steganography nowadays include hiding a secret piece of text within a photograph. Alternatively, you may hide a secret message or script inside a Word or Excel document.
In this work we will hide a .txt file inside an image.
### F5 Alogrithme
Is one of steganography algorithms who use compression to hide the files. 

### ----------------------------------------------------------------------------------------

## What we are going to see in this project?
In our project we implement two algorithme:
1. F5 algorithme in spacial and frequentiel domaine ( using JPEG compression).
2. JSTEG algorithme in spacial and frequentiel domaine ( using JPEG compression).

To hide a txt file inside an image.

In our project the insertion of secret message in frequentiel domaine is incorrect ( the hidding phase is supposed to be after compression and we send it in huffman form, and for extracting phase it is supposed to be after decoding huffman).

### ----------------------------------------------------------------------------------------
## What do you need to install to use this project?

### Flask:
```bash
>py -m pip install flask
```

#### Create an environment?
Linux :
```bash 
> sudo apt-get install python3-venv    # If needed
> python3 -m venv .venv
> source .venv/bin/activate
```
MacOS :
```bash 
> python3 -m venv .venv
> source .venv/bin/activate
```
Windows :
```bash 
> py -3 -m venv .venv
> .venv\scripts\activate
```

### Opencv:

```bash
>pip  install opencv-python
```

### HTML/ CSS/ JavaScript
