import math
from PIL import Image

#Discrete Cosine Transform, input a list, return flout list
def DCT(F):
    N=len(F)
    D=[[0 for i in range(N)] for i in range(N)]
    for u in range(0,N):
        for v in range(0,N):
            for x in range(0,N):
                for y in range(0,N):
                    D[u][v]=D[u][v]+F[x][y]*Phi(u,N)*Phi(v,N)*math.cos(math.pi*(x+0.5)*u/N)*math.cos(math.pi*(y+0.5)*v/N)
    return D

#Inverse Discrete Cosine Transform, input a list, return int list
def IDCT(D):
    N=len(D)
    F=[[0 for i in range(N)] for i in range(N)]
    for x in range(0,N):
        for y in range(0,N):
            for u in range(0,N):
                for v in range(0,N):
                    F[x][y]=F[x][y]+D[u][v]*Phi(u,N)*Phi(v,N)*math.cos(math.pi*(x+0.5)*u/N)*math.cos(math.pi*(y+0.5)*v/N)
            F[x][y]=int(round(F[x][y]))
    return F

#The factor in DCT and IDCT
def Phi(s,N):
    if s==0:
        phi=(1.0/N)**0.5
    else:
        phi=(2.0/N)**0.5
    return phi

#Divide a picture into 8*8 blocks, return a list of image with 2 dimension
def Divide(pic):
    print ("Divide the image into 8*8 blocks:")
    s=pic.size
    block_size=8
    row=int(s[0]/block_size)
    col=int(s[1]/block_size)
    block=[[0 for i in range(col)] for i in range(row)]
    i=0
    for x in range(0,row):
        for y in range(0,col):
            box=(x*block_size,y*block_size,(x+1)*block_size,(y+1)*block_size)
            block[x][y]=pic.crop(box)
    print ("Done.")
    return block

#Combine the blocks into a picture
def Combine(block):
    block_size=block[0][0].size
    row=len(block)
    col=len(block[0])
    pic=Image.new('RGB',(block_size[0]*row,block_size[1]*col))
    for x in range(0,row):
        for y in range(0,col):
            box=(x*block_size[0],y*block_size[0],(x+1)*block_size[0],(y+1)*block_size[0])
            pic.paste(block[x][y],box)
    return pic

#Convert the picture into YUV model, and pick out the 3 channel in matrix
def ChaMat(pic):
    pic=pic.convert('YCbCr')
    s=pic.size
    pic_Y,pic_Cb,pic_Cr=pic.split()
    M_Y=[[0 for i in range(s[1])] for i in range(s[0])]
    M_Cb=[[0 for i in range(s[1])] for i in range(s[0])]
    M_Cr=[[0 for i in range(s[1])] for i in range(s[0])]
    for x in range(s[0]):
        for y in range(s[1]):
            M_Y[x][y]=pic_Y.getpixel((x,y))
            M_Cb[x][y]=pic_Cb.getpixel((x,y))
            M_Cr[x][y]=pic_Cr.getpixel((x,y))
    return M_Y,M_Cb,M_Cr

#According to the matrix of YUV, draw a picture
def DrawMat(Y,Cb,Cr):
    s=[len(Y),len(Y[0])]
    pic=Image.new('YCbCr',(s[0],s[1]))
    for x in range(s[0]):
        for y in range(s[1]):
            pic.putpixel((x,y),(Y[x][y],Cb[x][y],Cr[x][y]))
    return pic

#Quantization by Q
def Quan(M,Q):
    s=[len(M),len(M[0])]
    for x in range(s[0]):
        for y in range(s[1]):
            M[x][y]=int(M[x][y]/Q)
    return M

#Dequantization by Q
def Dequan(M,Q):
    s=[len(M),len(M[0])]
    for x in range(s[0]):
        for y in range(s[1]):
            M[x][y]=M[x][y]*Q
    return M

#Division, DCT and quatization, output YUV channel for 8*8 blocks
def Compress(pic,Q):
    block=Divide(pic)
    block_size=block[0][0].size
    amount=[len(block),len(block[0])]
    Y=[[[[0 for i in range(block_size[1])] for i in range(block_size[0])] for i in range(amount[1])] for i in range(amount[0])]
    Cb=[[[[0 for i in range(block_size[1])] for i in range(block_size[0])] for i in range(amount[1])] for i in range(amount[0])]
    Cr=[[[[0 for i in range(block_size[1])] for i in range(block_size[0])] for i in range(amount[1])] for i in range(amount[0])]
    for x in range(amount[0]):
        print 'Compress: %d/%d' %(x+1,amount[0])
        for y in range(amount[1]):
            Y[x][y],Cb[x][y],Cr[x][y]=ChaMat(block[x][y])
            #DCT
            Y[x][y]=DCT(Y[x][y])
            Cb[x][y]=DCT(Cb[x][y])
            Cr[x][y]=DCT(Cr[x][y])
            if Q!=0:
                #Quantization
                Y[x][y]=Quan(Y[x][y],Q)
                Cb[x][y]=Quan(Cb[x][y],Q)
                Cr[x][y]=Quan(Cr[x][y],Q)
    print ("Compression done.")
    return Y,Cb,Cr

#Dequantization, IDCT and combination of blocks into one image
def Decompress(Y,Cb,Cr,Q):
    amount=[len(Y),len(Y[0])]
    block_size=[len(Y[0][0]),len(Y[0][0][0])]
    #print (amount,block_size)
    block=[[Image.new('YCbCr',(block_size[0],block_size[1])) for i in range(amount[1])]for i in range(amount[0])]
    for x in range(amount[0]):
        print 'Decompress: %d/%d' %(x+1,amount[0])
        for y in range(amount[1]):
            if Q!=0:
                #Dequantization
                Y[x][y]=Dequan(Y[x][y],Q)
                Cb[x][y]=Dequan(Cb[x][y],Q)
                Cr[x][y]=Dequan(Cr[x][y],Q)
            #DCT
            Y[x][y]=IDCT(Y[x][y])
            Cb[x][y]=IDCT(Cb[x][y])
            Cr[x][y]=IDCT(Cr[x][y])
            block[x][y]=DrawMat(Y[x][y],Cb[x][y],Cr[x][y])
    pic=Combine(block)
    print ('Decompression done')
    return pic
    
#Write a 4-dimensional matrix values into a text file
def Store(M,Name):
    Name=str(Name)
    print('Storing data into '+Name+'.txt')
    s=[len(M),len(M[0]),len(M[0][0]),len(M[0][0][0])]
    print(s)
    data=open(Name+'.txt','w')
    for i in range(len(s)):
        temp=str(s[i])
        data.writelines(temp+'\n')
    for x in range(s[0]):
        for y in range(s[1]):
            for u in range(s[2]):
                for v in range(s[3]):
                    temp=str(M[x][y][u][v])
                    data.writelines(temp+'\n')
    data.close()
    print('Done')
    return

#Read a 4-dimensional matrix values from a text file
def Load(Name):
    Name=str(Name)
    print('Loading data from '+Name+'.txt')
    s=[0,0,0,0]
    load=open(Name+'.txt')
    for i in range(len(s)):
        temp=load.readline()
        s[i]=int(temp)
    M=[[[[0 for i in range(s[3])]for i in range(s[2])]for i in range(s[1])]for i in range(s[0])]
    data=open(Name+'.txt')
    for x in range(s[0]):
        for y in range(s[1]):
            for u in range(s[2]):
                for v in range(s[3]):
                    temp=load.readline()
                    M[x][y][u][v]=float(temp)
    load.close()
    print('Done')
    return M

#Accoding to the matrix values from two frame, return the background  and forground pixel values
def Segment(Frame1,Frame2,alpha):
    print('Separating the background and foreground:')
    Frame1=str(Frame1)
    Frame2=str(Frame2)
    Y1=Load('Y'+Frame1)
    Cb1=Load('Cb'+Frame1)
    Cr1=Load('Cr'+Frame1)
    Y2=Load('Y'+Frame2)
    Cb2=Load('Cb'+Frame2)
    Cr2=Load('Cr'+Frame2)
    s=[len(Y1),len(Y1[0]),len(Y1[0][0]),len(Y1[0][0][0])]
    for x in range(s[0]):
        for y in range(s[1]):
            distance=[0,0,0]
            for u in range(s[2]):
                for v in range(s[3]):
                    Y1[x][y][u][v]=alpha*Y2[x][y][u][v]+(1-alpha)*Y1[x][y][u][v]
                    Cb1[x][y][u][v]=alpha*Cb2[x][y][u][v]+(1-alpha)*Cb1[x][y][u][v]
                    Cr1[x][y][u][v]=alpha*Cr2[x][y][u][v]+(1-alpha)*Cr1[x][y][u][v]
                    distance[0]=distance[0]+(Y2[x][y][u][v]-Y1[x][y][u][v])**2
                    distance[1]=distance[1]+(Cb2[x][y][u][v]-Cb1[x][y][u][v])**2
                    distance[2]=distance[2]+(Cr2[x][y][u][v]-Cr1[x][y][u][v])**2
            if distance[0]+distance[1]+distance[2]<17000:
                Y2[x][y]=[[0 for i in range(s[3])] for i in range(s[2])]
                Cb2[x][y]=[[0 for i in range(s[3])] for i in range(s[2])]
                Cr2[x][y]=[[0 for i in range(s[3])] for i in range(s[2])]
            else:
                print 'distance=%d' %(distance[0]+distance[1]+distance[2])
    print('Separation done')
    return Y1,Cb1,Cr1,Y2,Cb2,Cr2

#Compare the background and foreground to make a more elaborate foreground
def Compare(bg,fg):
    print('Comparing the pixel values:')
    size=bg.size
    Y1,Cb1,Cr1=ChaMat(bg)
    Y2,Cb2,Cr2=ChaMat(fg)
    for x in range(size[0]):
        for y in range(size[1]):
            if Y2[x][y]!=Y2[0][0] and Cb2[x][y]!=Cb2[0][0] and Cr2[x][y]!=Cr2[0][0]:
                diff=abs(Y1[x][y]-Y2[x][y])+abs(Cb1[x][y]-Cb2[x][y])+abs(Cr1[x][y]-Cr2[x][y])
                if diff<10:
                    Y2[x][y]=Y2[0][0]
                    Cb2[x][y]=Cb2[0][0]
                    Cr2[x][y]=Cr2[0][0]
                else:
                    print 'diff=%d' %(diff)
    pic=DrawMat(Y2,Cb2,Cr2)
    print('Done')
    return pic

Q=0
alpha=0.5
for i in range(1,10):
    print(i)
    background=Image.open('test00'+str(i)+'.jpg')
    Y,Cb,Cr=Compress(background,Q)
    Store(Y,'Y00'+str(i))
    Store(Cb,'Cb00'+str(i))
    Store(Cr,'Cr00'+str(i))

for i in range(1,9):
    Y_b,Cb_b,Cr_b,Y_f,Cb_f,Cr_f=Segment('00'+str(i),'00'+str(i+1),alpha)
    background=Decompress(Y_b,Cb_b,Cr_b,Q)
    background.save('test00'+str(i)+'_bg.jpg')
    foreground=Decompress(Y_f,Cb_f,Cr_f,Q)
    foreground.save('test00'+str(i)+'_fg.jpg')
    foreground=Compare(background,foreground)
    foreground.save('test00'+str(i)+'_fu.jpg')


