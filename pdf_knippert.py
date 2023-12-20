
import warnings
import os
import subprocess

import sys 
def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        return output.strip()
    except Exception as e:
        return f"Error: {str(e)}"

infile = sys.argv[1]
dir = os.getcwd()+"/"
# Example usage:

# dir = "/home/leander/OneDrive/master/YearTwo/MB/project/"
# infile = "liu_pnas(1).pdf"
if len(sys.argv)>2:
    page = int(sys.argv[2])
else:
    page = input("welke pagina? ")

plaatjes = input("Vector plaatje? (Y/n)")
if len(plaatjes)==0 or plaatjes.strip()[0].lower()=="y":
    pdf_setting = "screen"      # kleiner maar fuckt niet-vector plaatjes op
else:
    pdf_setting = "prepress"  #groter, maar fuckt plaatjes niet


select_page = 'pdftk "'+dir+infile+'" cat '+str(page)+' output '+dir+'single_page.pdf'

run_command(select_page)
import time 

command_to_run = 'pdfcrop '+dir+'single_page.pdf '+dir+'single_page.pdf --verbose'  # Replace this with the command you want to run
output = run_command(command_to_run)


lijn = [x for x in output.split("\n") if "HiRes" in x][0]

bbox = (list(map(float,lijn.replace("%%HiResBoundingBox: ","").split(" "))))

w = bbox[2]
h = bbox[3]

command_to_run = 'convert -density 200 '+dir+'single_page.pdf -background white -alpha remove -alpha off output.png'
output = run_command(command_to_run)



import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, RectangleSelector
from PIL import Image

warnings.filterwarnings("ignore", module="matplotlib")

class ImageSelectorApp:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)

        self.fig, self.ax = plt.subplots()
        self.ax.imshow(self.image)
        self.rect = Rectangle((0, 0), 1, 1, linewidth=1, edgecolor='r', facecolor='none')
        self.ax.add_patch(self.rect)

        self.selector = RectangleSelector(self.ax, self.onselect, useblit=True,
                                           button=[1], minspanx=5, minspany=5, spancoords='pixels',
                                           interactive=True)
        self.select_button = Button(plt.axes([0.8, 0.025, 0.1, 0.04]), 'Select Box')
        self.select_button.on_clicked(self.select_box)

        plt.show()

    def onselect(self, eclick, erelease):
        self.rect.set_width(erelease.xdata - eclick.xdata)
        self.rect.set_height(erelease.ydata - eclick.ydata)
        self.rect.set_xy((eclick.xdata, eclick.ydata))

        # Print or use the rectangle coordinates
        # print(f"Rectangle Coordinates: x={eclick.xdata:.2f}, y={eclick.ydata:.2f}, width={self.rect.get_width():.2f}, height={self.rect.get_height():.2f}")
        
        self.ax.figure.canvas.draw()

    def select_box(self, event):

        selected_box = self.rect.get_bbox()
        # print(selected_box)
        W = self.image.size[0]
        H = self.image.size[1]
        # print("Selected Box:", selected_box)
        x0, y0, x1, y1 = selected_box.x0, selected_box.y0, selected_box.x1, selected_box.y1
        print("bbox:", x0/W, y0/H, x1/W, y1/H)
        # print("w,h",w,h)
        m1 = x0*w/W
        m2 = y0*h/H 
        m3 = w-x1*w/W
        m4 = h-y1*h/H
        margins = str(-m1)+" "+str(-m2)+" "+str(-m3)+" "+str(-m4)
        # print(margins)
        select_page = 'pdftk "'+dir+infile+'" cat '+str(page)+' output '+dir+'single_page.pdf'

        run_command(select_page)

        command_to_run = 'pdfcrop "'+dir+'single_page.pdf" --verbose --margins "'+margins+'" --clip '+dir+'single_page.pdf'  # Replace this with the command you want to run

        output = run_command(command_to_run)
        output = run_command('pdftk '+dir+'single_page.pdf output '+dir+'single_page.pdf')
        output = run_command('pdfcrop '+dir+'single_page.pdf --margins 5 '+dir+'single_page.pdf')
        run_command('gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/'+pdf_setting+' -dNOPAUSE -dQUIET -dBATCH -sOutputFile='+dir+'Mooi_Uitgeknipt.pdf -r300 '+dir+'single_page.pdf')
        print("Plaatje is opgeslagen!")

if __name__ == "__main__":
    image_path = "output.png"  # Replace with the path to your image
    app = ImageSelectorApp(image_path)

os.remove(dir+'single_page.pdf')
os.remove(dir+'output.png')