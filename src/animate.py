#!/usr/bin/python3
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import math

# Sizes in pixels
networkWidth = 800
dynamicsWidth = 800
height = 800
padding = 40
nodeSize = 80
betweenNodes = 200
maxSize = 5000
couplingWidth = 10
textSize = 40
dpi = 50
barWidth = 50

# How often it should sample, 5 means create one frame every 5 genomes
skip = 1

# How long the gif should be in seconds
gifSeconds = 10

# Heatmap function, val between 0 and 1 -> colour tuple
def heatmap(val):

    # blue, cyan, green, yellow, red
    cols = [(0,0,255),(0,255,255),(0,255,0),(255,255,0),(255,0,0)]
    vals = [0.000,0.250,0.500,0.750,1.000]

    indexLow = int(val * 4.0)
    indexHigh = indexLow + 1

    if indexHigh >= len(vals): return cols[-1]

    ratio = (val-vals[indexLow])/(vals[indexHigh]-vals[indexLow])
    col = [int(cols[indexLow][i] + (cols[indexHigh][i]-cols[indexLow][i])*ratio) for i in range(3)]

    return tuple(col)

# Load data from file
genomes = []
fidelities = []
numSteps = 0
maxTime = 0
with open(sys.argv[1], "r") as f:
    for line in f:
        split = line.split()

        # First line should be the max time value
        if maxTime == 0:
            maxTime = float(split[0])

        # Second line should be the number of steps in the dynamics
        elif numSteps == 0:
            numSteps = int(split[0])

        # Then the rest should be genomes followed by dynamics data
        else:
            genomes.append(split[0])
            fidelities.append([])
            for val in split[1:]:
                fidelities[-1].append(float(val))

# Init image arrays
networkImages = []
dynamicsImages = []
combinedImages = []

# For each instance
for index in range(0, len(genomes), skip):

    # Create image for dynamics
    im1 = Image.new('RGB', (maxSize, maxSize), (255, 255, 255))
    draw1 = ImageDraw.Draw(im1)

    # Create empty coupling array
    couplings = [] 
    lettersAdded = {}
    genome = genomes[index]
    maxCoupling = -99999

    # Determine how many digits are used per coupling
    digitsPer = 0
    i = 2
    while genome[i] in "0123456789":
        digitsPer += 1
        i += 1
    visStart = genome.find("#")

    # Go through the genome 
    for i in range(0, visStart, 2+digitsPer):

        newCoupling = {}

        # If in ascii order, coupling is positive
        if ord(genome[i]) < ord(genome[i+1]):

            # Get the letters
            newCoupling["a"] = genome[i]
            newCoupling["b"] = genome[i+1]

            # Get the coupling val
            newCoupling["val"] = int(genome[i+2:i+2+digitsPer])

        # If in reverse ascii order, coupling is negative
        else:

            # Get the letters
            newCoupling["a"] = genome[i+1]
            newCoupling["b"] = genome[i]

            # Get the coupling val
            newCoupling["val"] = -int(genome[i+2:i+3+digitsPer])

        # Get the vis info
        newCoupling["dir"] = int(genome[visStart+1+int(i/(2+digitsPer))], 16) * 22.5 * (math.pi/180.0)

        if abs(newCoupling["val"]) > maxCoupling: maxCoupling = abs(newCoupling["val"])

        # Add to the couplings array
        couplings.append(newCoupling)

    # Add the first node 
    x = maxSize/2
    y = maxSize/2
    draw1.ellipse([x-nodeSize/2,y-nodeSize/2,x+nodeSize/2,y+nodeSize/2],fill=(0,0,0))
    lettersAdded[couplings[0]["a"]] = [x, y]

    # Keep track of min/max x/y values
    minX = x
    maxX = x
    minY = y
    maxY = y

    # Repeat to make sure all nodes placed
    for iteration in range(10):

        # For each coupling
        for coupling in couplings:

            # If the first node in the coupling has already been placed
            if coupling["a"] in list(lettersAdded.keys()) and coupling["b"] not in list(lettersAdded.keys()):
                prevX = lettersAdded[coupling["a"]][0]
                prevY = lettersAdded[coupling["a"]][1]
                x = prevX + math.cos(coupling["dir"])*betweenNodes
                y = prevY + math.sin(coupling["dir"])*betweenNodes
                draw1.line([prevX,prevY,x,y], fill=heatmap(coupling["val"]/maxCoupling), width=couplingWidth)
                draw1.ellipse([x-nodeSize/2,y-nodeSize/2,x+nodeSize/2,y+nodeSize/2],fill=(0,0,0))
                draw1.ellipse([prevX-nodeSize/2,prevY-nodeSize/2,prevX+nodeSize/2,prevY+nodeSize/2],fill=(0,0,0))
                lettersAdded[coupling["b"]] = [x, y]
                if x < minX: minX = x
                if x > maxX: maxX = x
                if y < minY: minY = y
                if y > maxY: maxY = y

            # If the second node in the coupling has already been placed
            elif coupling["b"] in list(lettersAdded.keys()) and coupling["a"] not in list(lettersAdded.keys()):
                prevX = lettersAdded[coupling["b"]][0]
                prevY = lettersAdded[coupling["b"]][1]
                x = prevX + math.cos(coupling["dir"])*betweenNodes
                y = prevY + math.sin(coupling["dir"])*betweenNodes
                draw1.line([prevX,prevY,x,y], fill=heatmap(coupling["val"]/maxCoupling), width=couplingWidth)
                draw1.ellipse([x-nodeSize/2,y-nodeSize/2,x+nodeSize/2,y+nodeSize/2],fill=(0,0,0))
                draw1.ellipse([prevX-nodeSize/2,prevY-nodeSize/2,prevX+nodeSize/2,prevY+nodeSize/2],fill=(0,0,0))
                lettersAdded[coupling["a"]] = [x, y]
                if x < minX: minX = x
                if x > maxX: maxX = x
                if y < minY: minY = y
                if y > maxY: maxY = y

            # If both nodes are there, draw the coupling anyway
            elif coupling["a"] in list(lettersAdded.keys()) and coupling["b"] in list(lettersAdded.keys()):
                prevX = lettersAdded[coupling["a"]][0]
                prevY = lettersAdded[coupling["a"]][1]
                x = lettersAdded[coupling["b"]][0]
                y = lettersAdded[coupling["b"]][1]
                draw1.line([prevX,prevY,x,y], fill=heatmap(coupling["val"]/maxCoupling), width=couplingWidth)
                draw1.ellipse([x-nodeSize/2,y-nodeSize/2,x+nodeSize/2,y+nodeSize/2],fill=(0,0,0))
                draw1.ellipse([prevX-nodeSize/2,prevY-nodeSize/2,prevX+nodeSize/2,prevY+nodeSize/2],fill=(0,0,0))

    # Crop so everything is centered, leaving space for the title and the colour bar
    im1 = im1.crop((minX-nodeSize, minY-nodeSize-textSize-padding, maxX+nodeSize, maxY+nodeSize+barWidth+padding+textSize))

    # Write the generation title above it
    draw1 = ImageDraw.Draw(im1)
    fnt = ImageFont.load_default()
    draw1.text((im1.size[0]/2-textSize*2.8,padding/2), "generation " + str(index), font=fnt, fill=(0,0,0))

    # Draw a heatmap bar
    fromEdge = padding+textSize*4
    for x in range(fromEdge, im1.size[0]-fromEdge):
        col = heatmap((x-fromEdge)/float(im1.size[0]-2*fromEdge))
        draw1.line([x, im1.size[1]-padding, x, im1.size[1]-padding-barWidth], fill=col, width=1)
    draw1.text((padding,im1.size[1]-padding-barWidth-textSize/4), "0% of\nmax", font=fnt, fill=(0,0,0))
    draw1.text((im1.size[0]-padding-textSize*3,im1.size[1]-textSize/4-padding-barWidth), "100% of\nmax", font=fnt, fill=(0,0,0))

    # Scale if too large
    if im1.size[0] > networkWidth:
        im1 = im1.resize((networkWidth, int(im1.size[1]*(networkWidth/im1.size[0]))))
    if im1.size[1] > height:
        im1 = im1.resize((int(networkWidth*(height/img1.size[1])), height))

    # Generate dynamics graph as in dynamics.py but with slight formatting tweaks
    x = np.linspace(0, maxTime, numSteps)
    y = np.array(fidelities[index])
    fig = plt.figure(figsize=((dynamicsWidth-padding*2)/dpi,(dynamicsWidth-padding*4)/dpi), dpi=dpi)
    ax1 = plt.subplot()
    plt.title("", fontsize=textSize)
    ax1.set_xlim([0, maxTime])
    ax1.set_ylim([0.0, 1.0])
    for axis in ['top','bottom','left','right']:
        ax1.spines[axis].set_linewidth(textSize/10)
    plt.plot(x,y,color='black',lw=textSize/10)
    ax1.tick_params(axis='y', labelsize=textSize)
    ax1.tick_params(axis='x', labelsize=textSize)
    plt.xlabel('$\mathrm{time \cdot J_{max}}$',fontsize=textSize,color='black')
    plt.ylabel("fidelity",fontsize=textSize,color='black')
    plt.tight_layout()

    # Convert this matplotlib image to a PIL image
    fig.canvas.draw()
    im2 = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    plt.close()

    # Create image for the combination
    im3 = Image.new('RGB', (dynamicsWidth+networkWidth+padding, height), (255, 255, 255))

    # Combine images
    im3.paste(im1, (padding, int(height/2-im1.size[1]/2)))
    im3.paste(im2, (networkWidth+padding*2, int(height/2-im2.size[1]/2)))

    # Use the first ones as the basis for the gif
    if index == 0:
        im1First = im1.copy()
        im2First = im2.copy()
        im3First = im3.copy()
    else:

        # Add all to arrays
        networkImages.append(im1.copy())
        dynamicsImages.append(im2.copy())
        combinedImages.append(im3.copy())

# Save gif
perFrame = (gifSeconds * 1000 * skip) / len(genomes)
im1First.save('network.gif', save_all=True, append_images=networkImages, optimize=True, duration=perFrame, loop=0)
im1First.save('networkStart.png')
networkImages[-1].save('networkEnd.png')
im2First.save('dynamics.gif', save_all=True, append_images=dynamicsImages, optimize=True, duration=perFrame, loop=0)
im3First.save('combined.gif', save_all=True, append_images=combinedImages, optimize=True, duration=perFrame, loop=0)
