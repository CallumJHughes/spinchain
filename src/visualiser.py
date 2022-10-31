#!/usr/bin/python3

import tkinter as tk
import sys
import random
import re
import math

# Window settings
width = 1400
height = 850
imageOffset = 30
lineThickness = 2
refresh_every = 5

numDigits = 4

class Application(tk.Frame):

    def __init__(self, master=None):

        tk.Frame.__init__(self, master)
        self.pack()

        self.initInfo = ""
        self.timeInfo = ""
        self.stored_genome = ""

        # Only refresh the canvas every so often
        self.draw_counter = 0

        # Load the image for the node (and the node when selected)
        self.node_image = tk.PhotoImage(file="node.png")
        self.node_sel_image = tk.PhotoImage(file="node_sel.png")

        # The bottom section containing the add button and the genome string
        bottom_frame2 = tk.Frame(self)
        bottom_frame2.pack(side = "bottom")
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side = "bottom")

        # The top section, where all the nodes will be drawn
        self.top_frame = tk.Canvas(self)
        self.top_frame["width"] = width
        self.top_frame["height"] = height - 70
        self.top_frame.bind("<ButtonPress-1>", self.clear_selected)
        self.top_frame.pack(side = "top")
        self.top_frame.bind("<ButtonPress-2>", self.add_node)

        # Create the genome string output
        self.genome_string = tk.Text(bottom_frame2, font=("Sans", 12))
        self.genome_string["width"] = 90
        self.genome_string["height"] = 2
        self.genome_string.pack(side = "right", pady=10)
        self.genome_string.bind('<Return>', self.process_enter)
        self.set_genome("")

        # The array of nodes to eventually populate
        self.nodes = []

        # The array of currently selected nodes
        self.selected = []

        # The array of connections between nodes to draw
        self.connections = []

        # If given a string as an argument, load it into a network
        if len(sys.argv) > 1 and len(sys.argv[1]) > 5:
            self.load_from_genome(sys.argv[1])
            self.draw_connections()

        # If given a string as the second argument, load it into a network 
        elif len(sys.argv) > 2 and len(sys.argv[2]) > 5:
            self.load_from_genome(sys.argv[2])
            self.draw_connections()

        # Otherwise just set the genome to be blank
        else:
            self.set_genome("")
            self.draw_connections()

    def int_to_hex(self, val):

        if val <= 9: return str(val)
        elif val == 10: return "A"
        elif val == 11: return "B"
        elif val == 12: return "C"
        elif val == 13: return "D"
        elif val == 14: return "E"
        elif val == 15: return "F"
        else: return "0"

    def hex_to_int(self, val):

        try:
            return int(val)
        except:
            if val == "A": return 10
            elif val == "B": return 11
            elif val == "C": return 12
            elif val == "D": return 13
            elif val == "E": return 14
            elif val == "F": return 15
            else: print("ERROR - " + val)

    # When the enter key is pressed inside the genome entry box
    def process_enter(self, event):
        genome = self.genome_string.get(1.0, tk.END).strip()
        if genome[0] == '"': genome = genome[1:]
        if genome[-1] == '"': genome = genome[:-1]
        self.set_genome(genome)
        self.load_from_genome(genome)

    # Change the text of the genome box
    def set_genome(self, new_genome):
        self.stored_genome = new_genome
        self.genome_string.delete(1.0, tk.END)
        if len(new_genome) > 2:
            self.genome_string.insert(tk.END, '"' + new_genome + '"')

    # Given a genome string, create a visualisation of the network
    def load_from_genome(self, gen):

        global numDigits

        # Strip any spaces and newlines
        gen = gen.replace("\n", "").replace(" ", "")

        # Output the genome that's about to be loaded
        print("Loading: \"" + gen + "\"")

        # Process the positional directive
        posDirect = re.search("#.+", gen)
        if posDirect is None:
            posDirect = ""
            newPos = ""
        else:
            newPos = posDirect.group(0)[1:]
        gen = re.sub("#.+", "", gen)

        # Process the initial/target directive
        initDirect = re.search("\<.+\>", gen)
        if initDirect is None:
            initDirect = ""
            self.initInfo = ""
        else:
            self.initInfo = initDirect.group(0)
        gen = re.sub("\<.+\>", "", gen)

        # Process the time directive
        timeDirect = re.search("@\d+(\.\d+)?", gen)
        if timeDirect is None:
            self.timeInfo = ""
            timeDirect = ""
        else:
            self.timeInfo = timeDirect.group(0)
        gen = re.sub("@\d+(\.\d+)?", "", gen)

        # Clear any existing nodes and connections
        if len(self.nodes) > 0:
            for i in range(len(self.nodes)):
                self.nodes[i].destroy()
            self.connections = []

        # Reset everything
        self.nodes = []
        numNodes = 0
        uniqueLetters = []

        # Determine the number of digits used
        numDigits = 0
        i = 2
        while i < len(gen) and gen[i] in "0123456789":
            numDigits += 1
            i += 1

        # Ensure it's at least somewhat valid
        if (len(gen))%(2+numDigits) != 0:
            print("Not a valid genome string")
            self.set_genome("")
            return

        # Determine how many nodes to create
        for i in range(0, len(gen), 2+numDigits):

            # If each letter hasn't been used yet
            if gen[i] not in uniqueLetters:
                uniqueLetters.append(gen[i])
                numNodes += 1
            if gen[i+1] not in uniqueLetters:
                uniqueLetters.append(gen[i+1])
                numNodes += 1

        # Load the nodes 
        for i in range(numNodes):
            self.add_node()
            self.nodes[-1].letter = uniqueLetters[i]

        # Load the connections
        for i in range(0, len(gen), 2+numDigits):

            # Get the value
            value = int(gen[i+2:i+2+numDigits])

            # If the letters are the wrong way round, make the coupling negative
            if ord(gen[i]) > ord(gen[i+1]):
                self.connections.append({"a": uniqueLetters.index(gen[i+1]), "b": uniqueLetters.index(gen[i]), 
                                         "val": -value, "dir": newPos[int(i/(2+numDigits))]})
            else:
                self.connections.append({"a": uniqueLetters.index(gen[i]), "b": uniqueLetters.index(gen[i+1]), 
                                         "val": value, "dir": newPos[int(i/(2+numDigits))]})

        deltaPix = 150

        # Assume the first node is in the centre
        positions = {1: [0.0,0.0]}

        # Repeat until all positions found
        maxIter = 5
        iteration = 1
        while len(positions.keys()) < numNodes and iteration < maxIter:

            # Go through the connections, finding the next connection with one known and one unknown position
            for i in range(len(self.connections)):

                con = self.connections[i]

                # If a already present but not b
                if con["a"] in positions.keys() and con["b"] not in positions.keys():
                    p = [positions[con["a"]][0], positions[con["a"]][1]]
                    theta = 22.5 * (self.hex_to_int(con["dir"])) * (math.pi / 180.0)
                    p[0] += deltaPix * math.cos(theta)
                    p[1] += deltaPix * math.sin(theta)
                    positions[con["b"]] = p

                # If b already present but not a
                elif con["a"] not in positions.keys() and con["b"] in positions.keys():
                    p = [positions[con["b"]][0], positions[con["b"]][1]]
                    theta = 22.5 * (self.hex_to_int(con["dir"])) * (math.pi / 180.0)
                    p[0] -= deltaPix * math.cos(theta)
                    p[1] -= deltaPix * math.sin(theta)
                    positions[con["a"]] = p

            iteration += 1

        # Determine min/max X/Y
        minX = 9999
        minY = 9999
        maxX = -9999
        maxY = -9999
        for i in positions.keys():
            x = positions[i][0]
            y = positions[i][1]
            if x > maxX: maxX = x
            if y > maxY: maxY = y
            if x < minX: minX = x
            if y < minY: minY = y

        # Shift the positions accordingly
        shiftX = -minX-(maxX-minX) / 2
        shiftY = -minY-(maxY-minY) / 2 - 75
        for i in positions.keys():
            positions[i][0] += shiftX
            positions[i][1] += shiftY

        # Update the positions
        for i in range(numNodes):
            self.nodes[i].place(x=positions[i][0], y=positions[i][1])

        # Show these newly generated connections
        self.draw_connections()

    # Add a draggable node to the list of nodes
    def add_node(self, event=None):

        # Create a new node
        self.nodes.append(tk.Label(self,borderwidth=0,compound="center",highlightthickness = 0 ))

        # Give it standard properties
        self.nodes[-1]["image"] = self.node_image
        self.nodes[-1].indexNum = len(self.nodes)-1
        self.nodes[-1].isInit = False
        self.nodes[-1].isTarget = False

        # Place it at the mouse cursor
        if event is not None:
            mouse_x = event.widget.winfo_pointerx() - self.winfo_rootx()
            mouse_y = event.widget.winfo_pointery() - self.winfo_rooty()
            self.nodes[-1].place(x=mouse_x-imageOffset, y=mouse_y-imageOffset)
        else:
            self.nodes[-1].place(relx=0.5, rely=0.5, anchor="center")

        # Determine the letter for this new node 
        letters = self.get_letter_sets()
        for node in self.nodes[:-1]:
            if node.letter in letters:
                letters.remove(node.letter)
        self.nodes[-1].letter = letters[0]

        # Make this node draggable
        self.set_draggable(self.nodes[-1])

        # Redraw everything
        self.draw_connections()

    # Make a widget draggable (i.e. the nodes)
    def set_draggable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.bind("<ButtonPress-3>", self.toggle_active)
        widget.configure(cursor="hand1")

    # When the mouse is dragged whilst holding a node
    def on_drag(self, event):

        # Make sure a node is being held
        if self.dragging is not None:

            # Move the widget being dragged to the location of the mouse
            mouse_x, mouse_y = event.widget.winfo_pointerxy()
            self.dragging.place(relx=0.5, rely=0.5, anchor="center")
            self.dragging.place(x=mouse_x-root.winfo_x()-width/2, 
                                y=mouse_y-root.winfo_y()-height/2)

        # Redraw
        if self.draw_counter > refresh_every:
            self.draw_counter = 1
            self.draw_connections()
        else:
            self.draw_counter += 1

    # When the mouse first starts dragging a node
    def on_start(self, event):

        # Get the widget below the cursor
        x, y = event.widget.winfo_pointerxy()
        self.dragging= event.widget.winfo_containing(x,y)

        # Stop selecting when dragging
        self.clear_selected()

    # When the mouse stops dragging a node
    def on_drop(self, event):

        # Stop dragging
        self.dragging = None

    # Clear any selected nodes
    def clear_selected(self, *args):

        for i in self.selected:
            self.get_node_with_id(i)["image"] = self.node_image
        self.selected = []

    # When a node is right-clicked
    def toggle_active(self, event):

        # Get the widget below the cursor
        x, y = event.widget.winfo_pointerxy()
        nodeIndex = event.widget.winfo_containing(x,y).indexNum

        # If selecting a node which has already been selected
        if nodeIndex in self.selected:
            self.toggle_connection()
            self.selected.remove(nodeIndex)
            self.get_node_with_id(nodeIndex)["image"] = self.node_image
        else:
            self.selected.append(nodeIndex)
            self.get_node_with_id(nodeIndex)["image"] = self.node_sel_image

        # If exactly two nodes are selected, toggle the coupling and clear selected
        if len(self.selected) == 2:
            self.toggle_connection()
            self.clear_selected()

    # Toggle the connection specified
    def toggle_connection(self):

        # Ensure exactly two nodes are selected
        if len(self.selected) == 2:

            found = False

            # Find the right connection and remove if existing
            for connection in self.connections:
                if ((connection["a"] == self.selected[0] and 
                        connection["b"] == self.selected[1]) 
                or (connection["a"] == self.selected[1] and 
                        connection["b"] == self.selected[0])):
                    self.connections.remove(connection)
                    found = True

            # If the connection isn't found, add it
            if not found:
                self.connections.append({"a": self.selected[0], 
                    "b": self.selected[1], "val": int(10**numDigits / 2)})

        elif len(self.selected) == 1:

            found = False

            # Find the right connection and remove if existing
            for connection in self.connections:
                if ((connection["a"] == self.selected[0] and 
                        connection["b"] == self.selected[0])):
                    self.connections.remove(connection)
                    found = True

            # If the connection isn't found, add it
            if not found:
                self.connections.append({"a": self.selected[0], 
                    "b": self.selected[0], "val": int(10**numDigits / 2)})


        # Refresh the view
        self.draw_connections()

    def get_node_with_id(self, nodeID):

        for node in self.nodes:
            if node.indexNum == nodeID:
                return node

    # Redraw all of the lines between nodes
    def draw_connections(self):

        # Clear the canvas
        self.top_frame.delete("all")
        self.top_frame.create_rectangle([0, 0, width, height], fill="white", outline="white")

        help_text = "RMB: toggle coupling between nodes\n" + \
                    "MMB: add node\n" + \
                    "LMB: move nodes"

        # Draw the help text to the top left
        self.top_frame.create_text(150, 50, font="Sans 11", text=help_text)

        # Draw each connection
        self.top_frame.update_idletasks()
        for con in self.connections:
            if con["val"] != 0:
                if con["a"] == con["b"]:
                    x1 = self.get_node_with_id(con["a"]).winfo_x() + imageOffset
                    y1 = self.get_node_with_id(con["a"]).winfo_y() + imageOffset
                    self.top_frame.create_oval([x1-20, y1-60, x1+20, y1-40], fill="white", outline="white")
                    self.top_frame.create_text(x1, y1-50, font="Sans 15", text=str(con["val"]))
                    self.top_frame.update_idletasks()
                else:
                    x1 = self.get_node_with_id(con["a"]).winfo_x() + imageOffset
                    y1 = self.get_node_with_id(con["a"]).winfo_y() + imageOffset
                    x2 = self.get_node_with_id(con["b"]).winfo_x() + imageOffset
                    y2 = self.get_node_with_id(con["b"]).winfo_y() + imageOffset
                    self.top_frame.create_line(x1, y1, x2, y2, width=lineThickness)
                    xMid = (x1+x2) / 2
                    yMid = (y1+y2) / 2
                    self.top_frame.create_oval([xMid-20, yMid-10, xMid+20, yMid+10], fill="white", outline="white")
                    self.top_frame.create_text(xMid, yMid, font="Sans 15", text=str(con["val"]))
                    self.top_frame.update_idletasks()

        # Draw the initial/target markers and the node labels
        for node in self.nodes:

            x = node.winfo_x() + imageOffset
            y = node.winfo_y() + imageOffset

            if node.isInit and node.isTarget:
                self.top_frame.create_oval([x-30, y-70, x+30, y-30], fill="white", outline="white")
                self.top_frame.create_text(x, y-60, font="Sans 13", text="init +\ntarget")

            elif node.isInit:
                self.top_frame.create_oval([x-20, y-70, x+20, y-30], fill="white", outline="white")
                self.top_frame.create_text(x, y-50, font="Sans 13", text="init")

            elif node.isTarget:
                self.top_frame.create_oval([x-30, y-70, x+30, y-30], fill="white", outline="white")
                self.top_frame.create_text(x, y-50, font="Sans 13", text="target")

            self.top_frame.create_oval([x-10, y+40, x+10, y+60], fill="white", outline="white")
            self.top_frame.create_text(x, y+50, font="Sans 13 bold", text=node.letter, fill="black")

        # Also update the genome 
        self.generate_genome()

    # Generate a genome from the system in memory
    def generate_genome(self):

        # Start with a blank string
        gen = ""
        self.set_genome("")
        lettersAsWritten = []

        if len(self.connections) <= 0:
            return

        # Go through each connection 
        for con in self.connections:

            # Only add the useful connections
            if con["val"] != 0:

                # Turn the indexes into ASCII
                aLetter = self.get_node_with_id(con["a"]).letter
                bLetter = self.get_node_with_id(con["b"]).letter

                # See which letter comes first in the alphabet
                if ord(aLetter) < ord(bLetter):
                    earlierLetter = aLetter
                    laterLetter = bLetter
                else:
                    earlierLetter = bLetter
                    laterLetter = aLetter

                # Ensure positive
                if con["val"] > 0:
                    value = str(con["val"])
                    firstLetter = earlierLetter
                    secondLetter = laterLetter
                else:
                    value = str(-con["val"])
                    firstLetter = laterLetter
                    secondLetter = earlierLetter

                # Keep track of the order letters are written
                if con["a"] not in lettersAsWritten: lettersAsWritten.append(con["a"])
                if con["b"] not in lettersAsWritten: lettersAsWritten.append(con["b"])

                # Ensure the value takes two characters (e.g. 1 -> "01")
                while (len(value) < numDigits):
                    value = "0" + value

                # Combine the contributions
                gen += firstLetter + secondLetter + value

        # Add the target and initial vectors
        if self.initInfo == "":
            self.initInfo = "<" + self.nodes[lettersAsWritten[0]].letter + "|" + self.nodes[lettersAsWritten[-1]].letter + ">"

        uncomString = "#"

        # For each connection
        for con in self.connections:

            # Turn the indexes into ASCII
            aLetter = self.get_node_with_id(con["a"]).letter
            bLetter = self.get_node_with_id(con["b"]).letter

            # Get the positions of those nodes
            if ord(aLetter) < ord(bLetter):
                posax = self.nodes[con["a"]].winfo_x()
                posay = self.nodes[con["a"]].winfo_y()
                posbx = self.nodes[con["b"]].winfo_x()
                posby = self.nodes[con["b"]].winfo_y()
            else:
                posbx = self.nodes[con["a"]].winfo_x()
                posby = self.nodes[con["a"]].winfo_y()
                posax = self.nodes[con["b"]].winfo_x()
                posay = self.nodes[con["b"]].winfo_y()

            # Determine the direction
            raw_theta = (180.0 / math.pi) * math.atan2(posby-posay,posbx-posax)
            if (raw_theta < 0): raw_theta += 360.0
            theta = raw_theta
            direction = self.int_to_hex(round(theta / 22.5))
            uncomString += str(direction)

        # Add the directives
        gen = self.timeInfo + self.initInfo + gen + uncomString

        # Update the text box 
        self.set_genome(gen)

    def dir_to_angle(self, direct):

        if direct <= 8:
            return float(direct) * (-90.0 / 4.0) * (math.pi / 180.0)
        else:
            return float(16-direct) * (90.0 / 4.0) * (math.pi / 180.0)

    # Determine the different letter sets
    def get_letter_sets(self):

        letters = []

        # Capital letters
        for i in range(1, 27, 1):
            letters.append(chr(i+64))

        # Lowercase letters
        for i in range(1, 27, 1):
            letters.append(chr(i+96))

        return letters

root = tk.Tk()

# Set the size of the window
root.minsize(width, height)
root.maxsize(width, height)

# Set the title of the window
root.title("Spin Chain Network Builder")

# Start the window
app = Application(master = root)
app.mainloop()
