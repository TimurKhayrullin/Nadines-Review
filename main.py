# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import tkinter as tk
from pdf2image import *
from PIL import Image, ImageTk, ImageGrab

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

from tkinter import filedialog
LARGE_FONT = ("Verdana", 12)


class NadinesReview(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        data = Model()

        self.title('Nadine\'s review')


        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, ChoosePDF, Editor):
            frame = F(container, self, data)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller, model):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Nadine's Review", font=LARGE_FONT)
        label.grid(row=0, column=0, sticky='ew')

        button = tk.Button(self, text="Create Nadine Quiz",
                           command=lambda: controller.show_frame(ChoosePDF))
        button.grid(row=1, column=0)

        button2 = tk.Button(self, text="Open Nadine Quiz")
        button2.grid(row=2, column=0)

        button3 = tk.Button(self, text="Quit")
        button3.grid(row=3, sticky='ew')

class ChoosePDF(tk.Frame):

    def __init__(self, parent, controller, model):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Choose The PDFs you would like to use, then assign a page range (inclusive)", font=LARGE_FONT)
        label.grid(row=0, column=1, sticky='ew')

        self.PDFFile = ''
        self.btnText = tk.StringVar()
        self.btnText.set('Choose File')

        label1 = tk.Label(self, text="File", font=LARGE_FONT)
        label1.grid(row=1, column=0)

        label2 = tk.Label(self, text="Range start", font=LARGE_FONT)
        label2.grid(row=1, column=1)

        label3 = tk.Label(self, text="Range end", font=LARGE_FONT)
        label3.grid(row=1, column=2)

        button1 = tk.Button(self, textvariable=self.btnText, command= self.askopenfilename)
        button1.grid(row=2, column=0)

        self.PDFPageStart = tk.Entry(self)
        self.PDFPageStart.grid(row=2, column=1)

        self.PDFPageEnd = tk.Entry(self)
        self.PDFPageEnd.grid(row=2, column=2)

        continueButton = tk.Button(self, text='Continue', command=lambda : (self.serealize(controller, model)))
        continueButton.grid(row=3, sticky='ew')

    def askopenfilename(self):
        self.PDFFile = filedialog.askopenfilename()
        self.btnText.set(self.PDFFile[self.PDFFile.rindex('/')+1:])
        self.PDFPageStart.select_clear()
        self.PDFPageEnd.select_clear()

    def addPDF(self):
        self.PDFButtons.append(tk.Button(self, text="Choose file", command=lambda: self.askopenfilename(self.PDFButtons.index(self))))

    def removePDF(self):
        pass

    def serealize(self, controller, model):
        model.filePath = self.PDFFile
        model.pageStart = int(self.PDFPageStart.get())
        model.pageEnd = int(self.PDFPageEnd.get())
        controller.show_frame(Editor)

class Model():

    def __init__(self):

        self.filePath = ''
        self.pageStart = 0
        self.pageEnd = 0

class Editor(tk.Frame):

    def __init__(self, parent, controller, model):
        tk.Frame.__init__(self, parent)

        # geometry is 1000x700



        scrollFrame = tk.Frame(self, width=225, height=700)
        scrollFrame.grid(row=0, column=0, rowspan=10, columnspan=3, sticky='nsew')

        scrollbar = tk.Scrollbar(scrollFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(scrollFrame, yscrollcommand=scrollbar.set)
        for i in range(1000):
            listbox.insert(tk.END, str(i))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar.config(command=listbox.yview)

        emptyFrame = tk.Frame(self, bg='blue', width=775, height=50)
        emptyFrame.grid(row=0, column=3, columnspan=7, rowspan=2)

        initButton = tk.Button(emptyFrame, text='load PDF', command= lambda :self.loadPDF(model))
        initButton.grid(row=0, column=0)

        zoomIn = tk.Button(emptyFrame, text='+', command=lambda: self.zoom(0.20))
        zoomIn.grid(row=0, column=1)

        zoomOut = tk.Button(emptyFrame, text='-', command=lambda: self.zoom(-0.20))
        zoomOut.grid(row=0, column=2)


        self.images = []
        self.rects = []

        MODES = [('Rect Tool', 'rect'), ('Nona', 'na')]

        self.tool = tk.StringVar()
        self.tool.set("na")  # initialize

        for text, mode in MODES:
            b = tk.Radiobutton(emptyFrame, text=text, variable=self.tool, value=mode)
            b.grid(row=0,column=3+MODES.index((text,mode)))

        canvasFrame = tk.Frame(self, bg='yellow', bd='4', width=1075, height=650)
        canvasFrame.grid_rowconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(0, weight=1)

        exportBtn = tk.Button(emptyFrame, text='Export', command=lambda: self.export(canvasFrame, controller))
        exportBtn.grid(row=0, column=6)

        canvasFrame.grid(row=2, column=3, rowspan=8, columnspan=7)

        self.cvScroll = tk.Scrollbar(canvasFrame, orient=tk.VERTICAL)
        self.cvScroll.grid(row=0, column=1, sticky=tk.N+tk.S)

        self.cvScrollx = tk.Scrollbar(canvasFrame, orient=tk.HORIZONTAL)
        self.cvScrollx.grid(row=1, column=0, sticky=tk.E + tk.W)

        self.x = self.y = 0

        self.cv = tk.Canvas(canvasFrame, width=1075, height=650, yscrollcommand=self.cvScroll.set, xscrollcommand=self.cvScrollx.set)
        self.cv.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        self.cvScroll.config(command=self.cv.yview)
        self.cvScrollx.config(command=self.cv.xview)



        # Rectangle stuff
        self.cv.bind("<ButtonPress-1>", self.on_button_press)
        self.cv.bind("<B1-Motion>", self.on_move_press)
        self.cv.bind("<ButtonRelease-1>", self.on_button_release)


        self.rect = None

        self.start_x = None
        self.start_y = None


    def loadPDF(self, model):

        for img in convert_from_path(model.filePath, first_page=model.pageStart, last_page=model.pageEnd):
            self.images.append(ImageTk.PhotoImage(img.resize((900, 1200), Image.ANTIALIAS)))

        self.cv.config(scrollregion=(0, 0, self.images[0].width(), self.images[0].height()))
        self.cv.create_image(0, 0, image=self.images[0], anchor=tk.NW)

    def zoom(self, percent):
        pass

    def on_button_press(self, event):
        if self.tool.get() != 'rect':
            return
        # save mouse drag start position
        self.start_x = self.cv.canvasx(event.x)
        self.start_y = self.cv.canvasy(event.y)

        # create rectangle if not yet exist
        # if not self.rect:
        self.rect = self.cv.create_rectangle(self.x, self.y, 1, 1, width= 2, outline='black')

    def on_move_press(self, event):
        if self.tool.get() != 'rect':
            return
        curX, curY = event.x, event.y

        # expand rectangle as you drag the mouse
        self.cv.coords(self.rect, self.start_x, self.start_y, self.cv.canvasx(curX), self.cv.canvasy(curY))

    def on_button_release(self, event):
        if self.tool.get() != 'rect':
            return
        self.rects.append(self.rect)

    def export(self, widget, controller):

        for r in self.rects:
            x0 = self.cv.canvasx(0)
            y0 = self.cv.canvasy(0)

            cvCoord = self.cv.coords(r)
            x = controller.winfo_rootx() + widget.winfo_x() + (cvCoord[0] - x0)
            y = controller.winfo_rooty() + widget.winfo_y() + (cvCoord[1] - y0)
            x1 = controller.winfo_rootx() + widget.winfo_x() +(cvCoord[2] - x0)
            y1 = controller.winfo_rooty() + widget.winfo_y() + (cvCoord[3] - y0)
            print((cvCoord[0] - x0), (cvCoord[1] - y0))
            print(widget.winfo_x(),  widget.winfo_y())
            print(controller.winfo_rootx(), controller.winfo_rooty())
            print(x, y, x1, y1)
            ImageGrab.grab((x, y, x1, y1)).convert('RGB').save("question" + str(self.rects.index(r)) + ".png")




app = NadinesReview()

app.geometry('1315x715')
app.mainloop()