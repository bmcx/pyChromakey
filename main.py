import cv2 
from PIL import Image,ImageChops
import numpy
import math
import os
import sys

def removeGreenScreen(infile,outfile, keyColor = None, tolerance = None):
    #open files
    inDataFG = Image.open(infile).convert('YCbCr')
    BG = Image.new('RGBA', inDataFG.size, (0, 0, 0, 0))
    #make sure values are set
    if keyColor == None:keyColor = inDataFG.getpixel((1,1))
    if tolerance == None: tolerance = [50,130]
    [Y_key, Cb_key, Cr_key] = keyColor
    [tola, tolb]= tolerance
    
    (x,y) = inDataFG.size #get dimensions
    foreground = numpy.array(inDataFG.getdata()) #make array from image
    maskgen = numpy.vectorize(colorClose) #vectorize masking function

    
    alphaMask = maskgen(foreground[:,1],foreground[:,2] ,Cb_key, Cr_key, tola, tolb) #generate mask
    alphaMask.shape = (y,x) #make mask dimensions of original image
    imMask = Image.fromarray(numpy.uint8(alphaMask))#convert array to image
    invertMask = Image.fromarray(numpy.uint8(255-255*(alphaMask/255))) #create inverted mask with extremes
    
    #create images for color mask
    colorMask = Image.new('RGB',(x,y),tuple([0,0,0]))
    allgreen = Image.new('YCbCr',(x,y),tuple(keyColor))

    colorMask.paste(allgreen,invertMask) #make color mask green in green values on image
    inDataFG = inDataFG.convert('RGB') #convert input image to RGB for ease of working with
    cleaned = ImageChops.subtract(inDataFG,colorMask) #subtract greens from input
    BG.paste(cleaned,(0,0),imMask)#paste masked foreground over background
    BG.save(outfile, "PNG") #save cleaned image
    
# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def colorClose(Cb_p,Cr_p, Cb_key, Cr_key, tola, tolb):  
    temp = math.sqrt((Cb_key-Cb_p)**2+(Cr_key-Cr_p)**2)
    if temp < tola:
        z= 0.0
    elif temp < tolb:
        z= ((temp-tola)/(tolb-tola))
    else:
        z= 1.0
    return 255.0*z

def writeLog(data,filename):
    #print(var)
    with open(filename, 'w') as out:
        out.write(str(data) + '\n')

# extract frames 
def frameCapture(path,type): 
    # Path to video file 
    vidObj = cv2.VideoCapture(path) #cv2 v3 or above
    # Used as counter variable 
    count = 0
    # checks whether frames were extracted 
    success = 1
    global length
    if vidObj.isOpened():
        length = int(vidObj.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = vidObj.get(cv2.CAP_PROP_FPS)
        width = vidObj.get(cv2.CAP_PROP_FRAME_WIDTH)   
        height = vidObj.get(cv2.CAP_PROP_FRAME_HEIGHT) 
        writeLog("Frame Width : "+str(width)+"\nFrame Height : "+str(height)+"\nFrame Rate : "+str(fps),"out\\footageInfo.txt")
        print ("\n" * 100)
        while count < length: 
            # vidObj object calls read 
            # function extract frames 
            success, image = vidObj.read() 
            # Saves the frames with frame-count 
            cv2.imwrite("imgseq\\"+ str(type) +"\\frame"+ str(count).zfill(6) +".png", image)
            print_progress(count, (length-1), prefix='Creating Image Sequence', suffix="[ Frame : "+ str(count).zfill(6) +" ]", decimals=1, bar_length=50)
            count += 1

def genOutput():
    global length
    count = 0
    print ("\n" * 100)
    for file in os.listdir("imgseq\\footage\\"):
        removeGreenScreen("imgseq\\footage\\"+str(file),"out\\"+str(file))
        print_progress(count, (length-1), prefix='Generating Output Files', suffix="[ File : "+str(file)+" ]", decimals=1, bar_length=50)
        count += 1

def grabInput():
    print ("~ A simple GreenScreen Removing tool")
    print ("~ Output wil be a PNG Sequence")
    footage = input("Enter Filename with extention (Ex.Footage.mp4) \n: ")
    return footage

def start(footage):
    global length
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f == footage:
            frameCapture(footage,"footage") 
            genOutput()
            print("\n"+length+" Files Generated successfully! Check the 'out' directory.")
            print("\nPress Enter to Exit.")
            input("")
            quit()
        else:
            print("File not found!!  Press Enter to Try Again.")
            print("Remember to copy the file into this folder.")
            input("")
            break


if __name__ == '__main__': 
    done = False
    length = 0
    while not done:
        footage = grabInput()
        start(footage)