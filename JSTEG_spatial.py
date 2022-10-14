import cv2
from matplotlib.pyplot import show
import numpy as np
import math

#! read a msg frome a .txt file
def file_str(file_name):
    with open(file_name, 'r') as myfile:
        message=myfile.read()
    return message
#! write a msg into a .txt file
def str_file(message,file_name):
    file1 = open(file_name, "w")
    file1.write(message)
    file1.close()

    return file1

def messageToBinary(message):
  if type(message) ==str:
    return ''.join([format(ord(i),"08b") for i in message])
  elif type (message)== bytes or type(message)== np.ndarray:
    return [format(i,"08b") for i in message]
  elif type (message)== int or type(message)== np.uint8:
    return format(message,"08b")
  else: 
    raise TypeError("Input type not supported")

def insert_pixel(pixel,bit):
    if(bit=='0'):
        if(int(pixel)%2!=0):#lsb =1
            pixel-=1
        
    else:#bit=1
        if(int(pixel)%2==0):
                pixel+=1
    return pixel


def hidedata(image,msg):
    img=cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    cy = img[:,:,0]
    ccr =  img[:,:,1]
    ccb =  img[:,:,2]
    
    msg+="###_!"
    index=0
    bin_msg=messageToBinary(msg)
    data_len=len(bin_msg)
    h,w=cy.shape[0],cy.shape[1]

    for i in range (0,h):
        for j in range(0,w):
            if (cy[i,j]==0):
                continue
            if (cy[i,j]==1):
                continue
            if(i%8==0):
                if(j%8==0):
                    continue
            
            if index <data_len:
                cy[i,j]= insert_pixel(cy[i,j],bin_msg[index])
                index+=1
            if index>= data_len:
                break
        if index>= data_len:
                break
    

    ycrcbo = cv2.merge((cy,ccr,ccb))
    img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)
    
    # img=add_padd(image,h,w)
    # print("--------------PSNR-----------------")
    # psnr,mse=PSNR(image,img2)
    # print("psnr",psnr,"mse",mse)
    # print("-----------------------------------")

    return img2


def extract_pixel(pixel):
    if ( int(pixel)%2==0):
        
            return "0"
    else:
            return "1"
  
def showData(image) :

    img=cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    cy = img[:,:,0]

    binary_data = ""
    
    h,w=cy.shape[0],cy.shape[1]
    for i in range(0,h):
        for j in range(0,w):
            if (cy[i,j]==0):
                continue
            if (cy[i,j]==1):
                continue
            if(i%8==0):
                if(j%8==0):
                    continue
           
            
            binary_data += extract_pixel(cy[i,j]) #extracting data from the least significant bit 

    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "###_!": #check if we have reached the delimeter which is "#####"
            break
    
    return decoded_data[:-5] #remove the delimeter to show the original hidden message

def add_padd(image,h,w):
    
    nh = np.float32(h)
    nw = np.float32(w)

    nbh = math.ceil(nh / 8)
    nbh = np.int32(nbh)

    nbw = math.ceil(nw / 8)
    nbw = np.int32(nbw)
    H = 8 * nbh
    W = 8 * nbw
    padded_img = np.zeros((H, W,3), dtype='float32')   
    padded_img[0:h, 0:w] = image[0:h, 0:w]

    return padded_img

def PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if (mse == 0):
        return 100
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr, mse

# message=file_str("message.txt")
# image=cv2.imread('image.png')
# img2=hidedata(image,message)
# msg=showData(img2)
# print(msg)

