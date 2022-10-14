import cv2
import numpy as np

#! ------------------------------------- PSNR --------------------------------------------------------------------------
import math
def PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    if (mse == 0):
        return 100
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr, mse
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

#! ------------------------------------- key construction part ----------------------------------------------------------
import random


def key(password) :

    random.seed(password,2)
    a=round(random.random()*100)
    if(a<10):
        return a
    return round(a/10)

def arr_index(password,nb_blocks,nbw,image,insert_blocks):
    # nb_blocks=nbw*nbh #nombre de blocks
    words=password.split()
    keys=[]
    pos=0
    while pos<len(words):
        a=key(words[pos])
        if a not in keys:
            if(a<nb_blocks):
                keys.append(a)
        pos+=1
    #to complete the reste of numbrs to fit the insert blocks....
    pos=0
    pas=0
    while(len(keys)<insert_blocks):
        if (pos+pas<len(keys)):
            a=keys[pos]+keys[pos+pas]
            i,j=img_index(a,nbw)
            if(a<nb_blocks):
                if a not in keys:
                    if(image[i,j]!=0):   
                        keys.append(a)
            pos+=1
        else: 
            pos=0
            pas+=1
    print(keys)
    return keys

# keys=arr_index("Hello! hope you are doing well",20,13,image,40)

def img_index(block,nbw):
    i=0
    j=0
    while(block>nbw): #avancer dans les lignes
        i+=8
        block-=nbw # pour reinitialisé le conteur de block de j
    j=8*(block-1)
    return i,j    
#! -----------------------------------------------------------------------------------------------------------------------    
 
#! --------------------------------------------- Insertion functions -----------------------------------------------------    



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
#! Convert message to binary
def msg2bin(message):
    if type(message) ==str:
        return ''.join([format(ord(i),"08b") for i in message])
    elif type (message)== bytes or type(message)== np.ndarray:
        return [format(i,"08b") for i in message]
    elif type (message)== int or type(message)== np.uint8:
        return format(message,"08b")
    else: 
        raise TypeError("Input type not supported")

#! Calcul k
#? capacity c
def capacity(image):
    #? count nb coef
    h, w = image.shape[0], image.shape[1]
    hdct=h*w
    #? count nb DC coef
    hdc=hdct/64
    #? count nb non zero AC coef
    h0=0
    #? count nb AC coef = 1 or -1
    h1=0
    for i in range(0,h):
        for j in range(0,w):
            if (int(image[i,j])==0):
                h0+=1
            elif(int(image[i,j])==1):
                h1+=1
            elif(int(image[i,j])==-1):
                h1+=1
    
    #* count the capacity 
    C=hdct-hdc-h0-(0.5*h1)
    return C

#? find k
def find_k(message, image):
     #? embedding Rate help us to determine the suitable k for certin l and C
    R=np.array([
        100.00,66.67,42.86,26.67,16.13
    ]) #each position of that array = k ( ex: i=0 k=1 n=1 R=100.00%)
    #? msg lenght
    l= len(message)
    #print("l",l)
    #? capacity
    c=capacity(image)
    #print("c",c)
    #? r
    r=l/c
    #print("before r",r)
    r=r*100 #pourcentage
    #print("after r",r)
    for i in range(1,5):
        a=R[i-1]
        b=R[i]
        if( r > b):
            if(r<=a):
                return i+1
    return 4 # dans le cas ou le message est trop petit on choisi le k = 5 ( n=31)

#! embed msg lenght and k
# ### bit == 0 dct%2==0:
#                      ! dct >0 dct
#                      ? dct <0 dct ++
# ### bit == 0 dct%2==1:
#                      * dct >0 dct--
#                      ! dct <0 dct 
# ### bit == 1 dct%2==0:
#                      * dct >0 dct--
#                      ! dct <0 dct 
# ### bit == 1 dct%2==1:
#                      ! dct >0 dct
#                      ? dct <0 dct ++
def insert_pixel(pixel,bit):
    if(bit=='0'):
        if(int(pixel)%2==0): #pair 
            if (pixel<0): #negatif on ajoute 1, positif on fait rien
                pixel+=1
        else: #pixel%2==1
            if(pixel>0): #positif on decremente, negatife on fait rien
                pixel-=1
    else: #bit=1
        if(int(pixel)%2==0):
            if(pixel>0): #positif on decremente, negatife on fait rien
                pixel -=1

        else:
            if(pixel<0):
                pixel+=1
    return pixel

#? embed L end K

def embed_lk(image,l,k):
    stego=image.copy()
    bin_l=bin(l)[2:].zfill(23)
    bin_k=format(k, "08b")
    bin_msg=str(bin_l)
    bin_msg=bin_k+bin_msg #add bin_k in the left to form 31 bits
    le=len(bin_msg)
    #print("bin",bin_msg)
    #? get size of the y matrix
    [h, w] = image.shape[0], image.shape[1]
    p=0

    for i in range(0,h):
        j=0
        while(j<w):
            if(p<le): # we didn't embed the whole msg

                #? verify if it is a DC coef
                if(i%8==0):
                    if(j%8==0):
                        j+=1
                        continue
                
                #? verify if the DCT coef not null ( dct!=0)
                if(int(image[i,j])==0):
                    j+=1
                    continue
                
                #? embed the msg bit into the pixel 
                stego[i,j]=insert_pixel(image[i,j],bin_msg[p])
                # print("(i",i,"j",j,")","bit:",bin_msg[p],"img: ",image[i,j],"new", stego[i,j])
                #? verify if the embeded data didn't affect the value of the dct and it becomes 0 (new_dct==0)
                #? if so we need to embed the data again in the next non null coef
                
                if(int(stego[i,j])==0):
                    j+=1
                    continue # to pass all the verifications 
                else:
                    p+=1
                    j+=1

            else: # we embeded the msg
                break #2nd loop (while)
        if(p>=le):
            break #1st loop (for)

    return stego, i,j

#! get and set LSB for matrix encoding
#? Get LSB of a pixel
def getLSB(pixel):
    #? F4 interpret the LSB of the negative number as the oposite to the LSB of the absolute value
    if(int(pixel)%2==0):
        if (pixel>0): # ex: 4
            return 0
        else: # ex -4
            return 1
    else:
        if(pixel>0): #ex: 15
            return 1
        else: #ex: -15
            return 0


def setLSB(pixel,bit):
    if(bit==0):
        if(int(pixel)%2!=0):
            if(pixel>0):#lsb =1
                pixel-=1
        else:
            if (pixel<0):#lsb =1
                pixel-=1
    else:#bit=1
        if(int(pixel)%2==0):
            if(pixel>0):#lsb=0
                pixel-=1
        else:
            if(pixel<0):#lsb=0
                pixel-=1
    return pixel
#! create array a

def create_a(size,image,array,index):
    a=np.zeros((3,size),dtype=int)
    pos=0 #array index 
    width=image.shape[1]
    nbw=int(width/8)
    
    while(pos<size):
        i,j=img_index(array[index],nbw) #index of DC coef of the block aray[pos]
        a[0,pos]=getLSB(image[i+2,j])
        a[1,pos]=i+2
        a[2,pos]=j
        pos=pos+1
        index+=1
    
    return a,i,j,index
  
#! hash and xor functions
#? xor function
def xor(bit1,bit2):
    bit1=str(bit1)
    bit2=str(bit2)
    y = int(bit1, 2)^int(bit2,2)
    return bin(y)[2:].zfill(len(bit2))

#? hash function
def hash(a,k):
    # j=bin(0)[2:].zfill(k)
    # f=int(a[0])*int(j)
    f=0
    width=a.shape[1]
    for i in range(1,width+1):
        j=bin(i)[2:].zfill(k)
        m=int(a[0,i-1])*int(j)
        f=xor(f,m)
    f=int(f,2)
    return bin(f)[2:].zfill(k)
#! -----------------------------------------------------------------------------------------------------------------------    

#! -------------------------------------------- Matrix encoding ----------------------------------------------------------
def matrix_encoding(img,message,password):
    img=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    image = img[:,:,0]
    cr =  img[:,:,1]
    cb =  img[:,:,2]
    
    #? len of msg
    print("start encoding--------")
    message=msg2bin(message)
    
    l=len(message)
    #print("msg",message)
    #? find k
    k=find_k(message,image)
    #? find n
    n=(2**k)-1
    #? embed l and k
    image,i,j=embed_lk(image,l,k)
    #print("(i=",i,', j= ',j,')')
    #? verifier si l est divisible par k sinon fill the blank with 0s in the left of the mesg
    if(l%k!=0):
        modulo=k-(l%k) #pour trouver le nombre de 0
        message=message.zfill(l+modulo)
    l=len(message)
    
    #print("k",k,"n",n,"l",l)

    hight,width=image.shape[0],image.shape[1]
    nbh=int(hight/8)
    nbw=int(width/8)
    nb_blocks=nbh*nbw
    nb=(int(l/k))*n
    index=0
    array=arr_index(password,nb_blocks,nbw,image,nb)
    p=0
    
    new=image.copy()
    j=0
    i=8
   
    while(i<hight):
        while(j<width):
            if(p<l):
                #? find a
                #save the start position ci and cj , for the shrinkage
                ci=i
                cj=j
                a,i,j,index= create_a(n,image,array,index)
                
                #? find w
                w=message[p:p+k]
                #? find f(a)
                f=hash(a,k)
              

                #? fin s
                s=str(xor(f,w))
                s=int(s,2)
                #print("s",s)
                if(s!=0):
                    s=s-1 # array a start with index 0
                    #change the value of a
                    if(a[0,s]==0): 
                        a[0,s]=1
                    else: 
                        a[0,s]=0
                        
                new[a[1,s],a[2,s]]=setLSB(image[a[1,s],a[2,s]],a[0,s])
                
                print("a'",a[0])
                if(int(new[a[1,s],a[2,s]])==0):  #? shrinkage
                    #in the case of new=0 we need to create the array a from the same position but we skip the 0 created. for that
                    #we need to create the array a from the new matrix not from the image ( so we can skip the new 0 created that is not
                    # in the old img)
                    while (int(new[a[1,s],a[2,s]])==0):
                        #? find the new a
                        a,i,j= create_a(n,new,ci,cj)
                        
                        # #? find w
                        
                        #? find f(a)
                        f=hash(a,k)
                        
                        #? fin s
                        s=str(xor(f,w))
                        s=int(s,2)
                        
                        if(s!=0):
                            s=s-1 # array a start with index 0
                            #change the value of a
                            if(a[0,s]==0): 
                                a[0,s]=1
                            else: 
                                a[0,s]=0
                                
                        new[a[1,s],a[2,s]]=setLSB(image[a[1,s],a[2,s]],a[0,s])
                                      
                p+=k
                     
            else:
                break

        j=0
        if(p>=l):
            break
    
    ycrcbo = cv2.merge((new,cr,cb))
    img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)
    cv2.imwrite("stegoy.png",np.uint8(img2))

    # print("--------------PSNR-----------------")
    # psnr,mse=PSNR(img,img2)
    # print("psnr",psnr,"mse",mse)
    print("-----------------------------------")
    return img2


# image1=cv2.imread('Images/emma.png')
# img=cv2.cvtColor(image1,cv2.COLOR_BGR2YCR_CB)
# y = img[:,:,0]
# cr =  img[:,:,1]
# cb =  img[:,:,2]

# image=matrix_encoding(y,"hello! my name is hiba","Hello hope you are doing well it's been a long time")

# ycrcbo = cv2.merge((image,cr,cb))
# img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)

# h,w=image1.shape[0],image1.shape[1]
#! -----------------------------------------------------------------------------------------------------------------------    

#! ------------------------------------------- Extraction functions -------------------------------------------------------    

#? extracting l and k
# for each pixel i'll extract the message bit from the LSB: 
# ! new_dct%2==0 : 
#               ?### bit == 0 ex_dct%2==0: dct >0 dct
#               ?### bit == 0 ex_dct%2==1: dct >0 dct-- 
#               *### bit == 1 ex_dct%2==0: dct <0 dct  
#               *### bit == 1 ex_dct%2==1: dct <0 dct ++
# ! new_dct%2==1 : 
#               *### bit == 0 ex_dct%2==0: dct <0 dct ++ 
#               *### bit == 0 ex_dct%2==1: dct <0 dct
#               ?### bit == 1 ex_dct%2==0: dct >0 dct--
#               ?### bit == 1 ex_dct%2==1: dct >0 dct
def exctract_bit(pixel):
    if(int(pixel)%2==0):
        if ( pixel >0):
            return "0"
        else: return "1"
    else:
        if ( pixel >0):
            return "1"
        else: return "0"
   
def extraction_lk(image):
    data=""
    #? get size of the y matrix
    [h, w] = image.shape[0], image.shape[1]
    p=0
    for i in range(0,h):
        for j in range(0,w):
            if(len(data)!=31):
                #? verify if it is a DC coef
                if(i%8==0):
                    if(j%8==0):
                        
                        continue
                
                #? verify if the DCT coef not null ( dct!=0)
                if(int(image[i,j])==0):
                    
                    continue
                data+= exctract_bit(image[i,j])
                # print("(i",i,"j",j,")","img: ",image[i,j])                
            else:
                break
        if(len(data)==31):
            break
    k= data[:8]
    #print("bin k",k)

    l=data[8:]
    #print("bin l",l)
    k=int(k,2)
    l=int(l,2)
    return k,l,j,i

#? bin to msg
def char(binary_data):
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
    return decoded_data

#! -----------------------------------------------------------------------------------------------------------------------    
#! -------------------------------------------- Matrix decoding ----------------------------------------------------------

def matrix_decoding(image,password):
    img = cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    image = img[:,:,0]
    k,l,j,i=extraction_lk(image)
   
    if(l%k!=0):
        modulo=k-(l%k)
        le=l+modulo
    else:
        le=l
    #? find n
    n=(2**k)-1
    
    pos=0
    message=""
    hight,width=image.shape[0], image.shape[1]
    nbh=int(hight/8)
    nbw=int(width/8)
    nb_blocks=nbh*nbw
    nb=(int(l/k))*n
    array=arr_index(password,nb_blocks,nbw,image,nb)
    index=0
    
    j=0
    i=8
   
    while (i<hight):

        while(j<width):
            if(pos!=le):
                #? find a
                a,i,j,index=create_a(n,image,array,index)
                print("a''",a[0,:])
                
                #? find f(a)
                f=hash(a,k)
                print("(i",i,"j",j,"f",f,")")
                
                message+=str(f)
                pos+=k
            else:
                break
            # j+=1
        j=0
        # i+=1
        if(pos==le):
            break
    if(l%k!=0):
        p=modulo
    else: 
        p=0
    #print("bin msg",message[p:])
    message=char(message[p:]) #remove 0s added in the left
    #print("the msg",message)
    str_file(message,"extracted_data.txt")
    print(message)
    return message
    


# stego1 = cv2.cvtColor(img2,cv2.COLOR_BGR2YCR_CB)
# stego_y = stego1[:,:,0]
# stego_cr =  stego1[:,:,1]
# stego_cb =  stego1[:,:,2]

# k,l,j,i=extraction_lk(stego_y)

# print("afer extraction: k",k,"l",l,"i",i,"j",j)
# msg=matrix_decoding(stego_y,"Hello hope you are doing well it's been a long time")