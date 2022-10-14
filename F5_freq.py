import cv2
import numpy as np
from compression import *
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
    C=hdct+hdc-h0-(0.5*h1)
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
    return 5 # dans le cas ou le message est trop petit on choisi le k = 5 ( n=31)

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
def create_a(size,image, i, j):
    a=np.zeros((3,size),dtype=int)
    pos=0 #array index 
    height,width=image.shape[0],image.shape[1]
    if(j>=width):
        j=0
        i+=1
    while(pos<size ):
        if(j>=width):
            if( i<height):
                # break
                # pos=0 #reintialisation de l'indice du tableau a
                i+=1
                j=0
            else:
                raise Exception
                break
        #skip DC
        if(i%8==0):
            if(j%8==0):
                j+=1
                continue
        #skip pixels=0
        if(int(image[i,j])!=0):     
            if(int(image[i,j])!=-1):
                if(int(image[i,j])!=1):
                    a[0,pos]=getLSB(image[i,j])
                    a[1,pos]=i
                    a[2,pos]=j
                    pos=pos+1
        j=j+1
   
    return a,i,j
  
def create_xa(size,image, i, j):
    a=np.zeros((3,size),dtype=int)
    pos=0 #array index 
    hight,width=image.shape[0],image.shape[1]
    #make limite
    bh=i+1 
    bw=j+1 
    while(pos<size ): 
        if(j==bw):
            if(i==bh): #get the next block 
                # i=(bh-3)+8
                j=(bw-3)+8
                continue
            else:
                j=bw
                i+=1


        if(j>=width):
            if( i<hight):
                # break
                # pos=0 #reintialisation de l'indice du tableau a
                i+=8
                j=0
            else:
                raise Exception
                break
        #skip DC
        if(i%8==0):
            if(j%8==0):
                j+=1
                # continue
        #skip pixels=0
        if(int(image[i,j])!=0):     
                a[0,pos]=getLSB(image[i,j])
                a[1,pos]=i
                a[2,pos]=j
                pos=pos+1
        j=j+1
   
    return a,i,j
  
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

#! Matrix encoding
def matrix_encoding(image,message):
    img=cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)
    y = img[:,:,0]
    cr =  img[:,:,1]
    cb =  img[:,:,2]
    image=compression(y,QY)
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
    p=0
    
    new=image.copy()
    # if(j>=width):
    j=0
    i=8
    # else:
    #     i+=1
    while(i<hight):
        while(j<width):
            if(p<l):
                #? find a
                #save the start position ci and cj , for the shrinkage
                ci=i
                cj=j
                a,i,j= create_a(n,image,i,j)
                # #print('a ',a[0,:])
                #print("\n (i",i,"j",j,") \n")
                #? find w
                w=message[p:p+k]
                #? find f(a)
                f=hash(a,k)
                # #print('f',f)
                #print('(w',w,'f',f,')')

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
                
                # #print("a'",a[0,:])
                #print("(nw ",new[a[1,s],a[2,s]],' , img',image[a[1,s],a[2,s]],' , i:',a[1,s],', j: ', a[2,s],')')
                
                if(int(new[a[1,s],a[2,s]])==0):  #? shrinkage
                    #in the case of new=0 we need to create the array a from the same position but we skip the 0 created. for that
                    #we need to create the array a from the new matrix not from the image ( so we can skip the new 0 created that is not
                    # in the old img)
                    while (int(new[a[1,s],a[2,s]])==0):
                        #? find the new a
                        a,i,j= create_a(n,new,ci,cj)
                        #print("(i",i,"j",j,")")
                        # #? find w
                        # w=message[p:p+k]
                        #? find f(a)
                        f=hash(a,k)
                        # #print('f',f)
                        #? fin s
                        s=str(xor(f,w))
                        s=int(s,2)
                        #print('(w',w,'f',f,", s",s,')')
                        if(s!=0):
                            s=s-1 # array a start with index 0
                            #change the value of a
                            if(a[0,s]==0): 
                                a[0,s]=1
                            else: 
                                a[0,s]=0
                                
                        new[a[1,s],a[2,s]]=setLSB(image[a[1,s],a[2,s]],a[0,s])
                        #print("new",new[a[1,s],a[2,s]]," img",image[a[1,s],a[2,s]],' , i:',a[1,s],', j: ', a[2,s])
                
                p+=k
                     
            else:
                break
            # j+=1
            #j=j+n
        
        # i+=1
        j=0
        if(p>=l):
            break
    qy=decompression(new,QY)
    ccr=compression(cr,QC)
    qcr=decompression(ccr,QC)
    ccb=compression(cb,QC)
    qcb=decompression(ccb,QC)
    ycrcbo = cv2.merge((qy,qcr,qcb))
    img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)
    cv2.imwrite("stegoy.png",np.uint8(img2))

    return img2

# image1=cv2.imread('Images/peppers.tif')
# image2=cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
# message=file_str("encoded_data.txt")
# img=matrix_encoding(image2,message)

# image1=cv2.imread('Images/peppers.tif')
# img=cv2.cvtColor(image1,cv2.COLOR_BGR2YCR_CB)
# y = img[:,:,0]
# cr =  img[:,:,1]
# cb =  img[:,:,2]
# u=compression(y,QY)
# # print("u comp1")
# # printmat(u)
# image=matrix_encoding(u,"hello hope u r doing well")
# # print("insert comp1")
# # printmat(image)
# qy=decompression(image,QY)
# # # cv2.imshow("qy",qy)
# # # cv2.waitKey(0)
# ccr=compression(cr,QC)
# qcr=decompression(ccr,QC)
# ccb=compression(cb,QC)
# qcb=decompression(ccb,QC)
# ycrcbo = cv2.merge((qy,qcr,qcb))
# img2=cv2.cvtColor(ycrcbo,cv2.COLOR_YCR_CB2BGR)
# # cv2.imshow("img2",img2)
# # cv2.waitKey(0)
# h,w=image1.shape[0],image1.shape[1]
# decoded_img = img2[0:int(h),0:int(w),:]
# print("--------------PSNR-----------------")
# psnr,mse=PSNR(image1,decoded_img)
# print("psnr",psnr,"mse",mse)
# #! --------------- Matrix decoding ------------------------

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

def matrix_decoding(image):
    k,l,j,i=extraction_lk(image)
    #print("(i=",i,', j= ',j,')')
    #print("k",k,"l",l)
    if(l%k!=0):
        modulo=k-(l%k)
        le=l+modulo
    else:
        le=l
    #? find n
    n=(2**k)-1
    #print("n",n)
    pos=0
    message=""
    hight,width=image.shape[0], image.shape[1]
   
    # if(j>=width):
    j=0
    i=8
    # else:
    #     i+=1
    while (i<hight):

        while(j<width):
            if(pos!=le):
                #? find a
                a,i,j=create_a(n,image,i,j)
                # #print("a''",a[0,:])
                
                #? find f(a)
                f=hash(a,k)
                #print("(i",i,"j",j,"f",f,")")
                
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
    # str_file(message,"extracted_data.txt")
    return message
    

# matrix_decoding(img)
# # d=extraction_lk(img)
# # print("dat ",d)
# cv2.imshow("img",img)
# cv2.waitKey(0)



# stego1 = cv2.cvtColor(img2,cv2.COLOR_BGR2YCR_CB)
# stego_y = stego1[:,:,0]
# stego_cr =  stego1[:,:,1]
# stego_cb =  stego1[:,:,2]
# uy=compression(stego_y,QY)
# k,l,j,i=extraction_lk(uy)
# print("u comp2")

# print("afer extraction: k",k,"l",l,"i",i,"j",j)
# msg=matrix_decoding(uy)
# print(msg)