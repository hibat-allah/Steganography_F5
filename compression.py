#! ------------------------ ZigZag -----------------------------
#! ------------------------ Compression -------------------------
import numpy as np
import math
import cv2
#? strat compression and stop in quantization
def compression(img,QUANTIZATION_MAT):
    block_size=8
    # get size of the image
    [h, w] = img.shape[0], img.shape[1]

    # No of blocks needed : Calculation
    height = h
    width = w
    h = np.float32(h)
    w = np.float32(w)

    nbh = math.ceil(h / block_size)
    nbh = np.int32(nbh)

    nbw = math.ceil(w / block_size)
    nbw = np.int32(nbw)

    # Pad the image
    # height of padded image
    H = block_size * nbh

    # width of padded image
    W = block_size * nbw

    # create a numpy zero matrix with size of H,W
    padded_img = np.zeros((H, W), dtype='float32')   
    padded_img[0:height, 0:width] = img[0:height, 0:width]

    for i in range(nbh):
        row_ind_1 = i * block_size
        row_ind_2 = row_ind_1 + block_size

        for j in range(nbw):
            col_ind_1 = j * block_size
            col_ind_2 = col_ind_1 + block_size
            block = padded_img[row_ind_1: row_ind_2, col_ind_1: col_ind_2]

            # apply 2D discrete cosine transform to the selected block
            DCT = cv2.dct(block)

            #quantization
            DCT_normalized = np.divide(DCT, QUANTIZATION_MAT)#.astype(int)
        
            padded_img[row_ind_1: row_ind_2, col_ind_1: col_ind_2] = DCT_normalized

    # cv2.imshow('encoded image', np.uint8(padded_img))
    return padded_img

#! ------------------------ Decompression -------------------------
def decompression(qnt,QUANTIZATION_MAT):
    block_size=8
    # loop for constructing intensity matrix form frequency matrix (IDCT and all)
    i = 0
    j = 0
    k = 0
    h,w=qnt.shape[0],qnt.shape[1]
    # initialisation of compressed image
    padded_img = np.zeros((h,w))

    while i < h:
        j = 0
        while j < w:        
            block=qnt[i:i+8,j:j+8]
            de_quantized = np.multiply(block,QUANTIZATION_MAT)                
            idct = cv2.idct(de_quantized).clip(0, 255)        
            padded_img[i:i+8,j:j+8]=idct
            j = j + 8        
        i = i + 8

    # clamping to  8-bit max-min values
    padded_img[padded_img > 255] = 255
    padded_img[padded_img < 0] = 0

    
    # compressed image is written into compressed_image.mp file
    cv2.imwrite("compressed_image.bmp",np.uint8(padded_img))
    # cv2.imshow("compressed", np.uint8(padded_img))
    # cv2.waitKey(0)
    return np.uint8(padded_img)

QntY = np.array(
        [[16, 11, 10, 16, 24, 40, 51, 61], 
        [12, 12, 14, 19, 26, 58, 60, 55], 
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62], 
        [18, 22, 37, 56, 68, 109, 103, 77], 
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101], 
        [72, 92, 95, 98, 112, 100, 103, 99]])

QntC=np.array(
    [[17, 18, 24, 47, 99, 99, 99, 99],  # chrominance quantization table
                    [18, 21, 26, 66, 99, 99, 99, 99],
                    [24, 26, 56, 99, 99, 99, 99, 99],
                    [47, 66, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99]])
def qunatization_mat(Q):
    l=100-95
    l=l/50
    Q=Q*l
    return Q
QY=qunatization_mat(QntY)
QC=qunatization_mat(QntC)
