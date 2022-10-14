import numpy as np
from compression import *
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
        if pixel < 0 :
            pixel = pixel *-1
            test=int((pixel//10)%10)
            if test % 2 !=0: #lsb =1
                pixel=pixel-10
            pixel = pixel * -1
        else :
            test=int((pixel//10)%10)
            if test % 2 !=0: #lsb =1
                pixel=pixel-10
    else:#bit=1
        if pixel<0 :
            pixel = pixel * -1
            test=int((pixel//10)%10)
            if test % 2 ==0: #lsb =1
                pixel=pixel+10
            pixel = pixel * -1
        else :
            test=int((pixel//10)%10)
            if test % 2 ==0:
            # while ( (pixel%100)%2==0 and (pixel%10)!=5):
                pixel=pixel+10
    return pixel



def hidedata(image,msg):
    image1=image
    img = cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    y = img[:,:,0]
    cr =  img[:,:,1]
    cb =  img[:,:,2]
    y=y-128
    cr=cr-128
    cb=cb-128
    image=compression(y,QY)
    r=compression(cr,QY)
    b=compression(cb,QY)
    msg+="#"
    index=0
    bin_msg=messageToBinary(msg)
    # print("binmsg",bin_msg)
    data_len=len(bin_msg)
    h,w=image.shape[0],image.shape[1]

    for i in range (1,h,8):
        for j in range(1,w,8):
            if (image[i,j]==0):
                continue
            if (image[i,j]==1):
                continue
            if(i%8==0):
                if(j%8==0):
                    continue
            
            # bin_y=messageToBinary(cy[i,j])
            if index <data_len:
                image[i,j]= insert_pixel(image[i,j],bin_msg[index])
                index+=1
            if index>= data_len:
                break
        if index>= data_len:
                break
    
    decy=decompression(image,QY)
    decy=decy+128
    decr=decompression(r,QY)
    decr=decr+128
    decb=decompression(b,QY)
    decb=decb+128
    ycrcbo = cv2.merge((decy,decr,decb))
    img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)

    cv2.imwrite("stegoy.png",np.uint8(img2))
    # img=add_padd(image1,h,w)
    # print("--------------PSNR-----------------")
    # psnr,mse=PSNR(image1,img2)
    # print("psnr",psnr,"mse",mse)
    # print("-----------------------------------")
    return img2

def extract_pixel(pixel):
    if pixel < 0:
        pixel = pixel * -1
        test=int((pixel//10)%10)
        if test %2 ==0:
            return "0"
        else :
            return "1"
    else :
        test=int((pixel//10)%10)
        if (test%2==0):
        
            return "0"
        else:
            return "1"

def showData(image) :
    img3 = cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    y = img3[:,:,0]
    y=y-128
    image=compression(y,QY)
    binary_data = ""
    
    h,w=image.shape[0],image.shape[1]
    for i in range(1,h,8):
        for j in range(1,w,8):
            if (image[i,j]==0):
                continue
            if (image[i,j]==1):
                continue
            if(i%8==0):
                if(j%8==0):
                    continue
           
            
            binary_data += extract_pixel(image[i,j]) #extracting data from the least significant bit 

    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-1:] == "#": #check if we have reached the delimeter which is "#####"
            break
    return decoded_data[:-1] #remove the delimeter to show the original hidden message

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
