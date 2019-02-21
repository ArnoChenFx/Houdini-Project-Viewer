import os
import hou
from PySide2 import (QtWidgets, QtUiTools, QtGui, QtCore)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class ProjectViewer(QtWidgets.QWidget):
    def __init__(self):
        super(ProjectViewer, self).__init__()

        self.scriptpath = os.path.dirname(os.path.realpath(__file__))

        pathfile = open(self.scriptpath + "/ARNO_ProjV/Proj_Path.txt")
        txtcon = pathfile.readline()
        pathfile.close()
        self.oripath = txtcon.replace('\\','/')
        self.proj = self.oripath
        self.transition = "0";

        #load UI file
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.scriptpath+"/UI.ui")

        #get UI elements
        self.setproj = self.ui.findChild(QtWidgets.QPushButton, "setproj")
        self.folderlist = self.ui.findChild(QtWidgets.QComboBox, "folderlist")
        self.scenelist = self.ui.findChild(QtWidgets.QListWidget, "scenelist")
        self.label = self.ui.findChild(QtWidgets.QLabel, "label_2")
        self.height = self.ui.findChild(QtWidgets.QSpinBox, "spinbox")
        self.save = self.ui.findChild(QtWidgets.QPushButton, "save")


        # creat connections
        self.setproj.clicked.connect(self.setproject)
        self.folderlist.activated.connect(self.Refresh)
        self.folderlist.activated.connect(self.CreateInterface)
        self.height.valueChanged.connect(self.changeHeight)
        self.save.clicked.connect(self.saveproject)
        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)

        #add widgets to layout
        self.setLayout(mainLayout)

        # creat widgets
        self.Refresh()
        self.CreateInterface()

        #set icon size
        self.scenelist.setIconSize(QSize(150,150))
        self.label.setMaximumHeight(200)
        #set height
        heightfile = open(self.scriptpath + "/ARNO_ProjV/Height.txt")
        heightS = heightfile.readline()
        try:
            height = int(heightS)
        except ValueError:
            height = 500
        self.scenelist.setMaximumHeight(height)
        self.scenelist.setMinimumHeight(height)
        self.height.setValue(height)

        heightfile.close()

    def changeHeight(self,data):
        self.scenelist.setMaximumHeight(data)
        self.scenelist.setMinimumHeight(data)
        f = open(self.scriptpath + "/ARNO_ProjV/Height.txt", "wt")
        f.write(str(data))
        f.close()

    def saveproject(self):
        # get view port
        cur_desktop = hou.ui.curDesktop()
        scene = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        #save HIP
        a = hou.hipFile.name()
        k = a.split("/")
        hip = ''
        if len(k)==1:
            hip = hou.ui.selectFile(title='Save',file_type=hou.fileType.Hip)
            if hip!='':
                hou.hipFile.save(file_name = hip)
        else:
             hou.hipFile.save()
             hip = '1'

        if hip!='':
            #set name and path
            f = hou.frame()
            fn = hou.hipFile.basename().split(".")
            del fn[-1]
            filename = ".".join(fn)
            
            path=hou.hipFile.path().split("/")
            del path[-1]
            filepath = "/".join(path)+"/"+filename+".jpg"
            
            #getFlipbook
            flip_options = scene.flipbookSettings().stash()
            
            #SetFlipbook
            flip_options.frameRange((f, f))
            flip_options.outputToMPlay(0)
            flip_options.useResolution(1)
            flip_options.resolution((500,500))
            flip_options.output(filepath)
            
            #RunFlipbook
            scene.flipbook(scene.curViewport(), flip_options)
            
            print "Succeed!"

    def setproject(self):
        setpath = hou.ui.selectFile(title="Set Project",file_type=hou.fileType.Directory)
        newpath = os.path.dirname(setpath) +"/"

        if (newpath != "/"):
            self.proj = newpath
            f = open(self.scriptpath + "/ARNO_ProjV/Proj_Path.txt","wt")
            f.write(newpath)
            f.close()

        #print self.proj
        self.Refresh()
        self.CreateInterface()

    def Refresh(self):
        if self.proj != self.transition and self.proj !="":
            self.folderlist.clear()
            for folder in os.listdir(self.proj):
                self.folderlist.addItem(folder)

            self.transition = self.proj

        self.projpath = self.proj + str(self.folderlist.currentText())+"/"

        #print self.texpath

    def CreateInterface(self):
        self.scenelist.clear()

        try:
            for file in os.listdir(self.projpath):
                if file.endswith('.jpg'):
                    fn = file.split(".")
                    del fn[-1]
                    name = ".".join(fn)

                    #add icon
                    instex0 = self.projpath + file
                    jpg0 = QtGui.QPixmap(instex0).scaled(200, 200)
                    icon = QtGui.QIcon(jpg0)
                    item = QListWidgetItem(icon, "")
                    item.setText(name)
                    item.setMinimumWeight = 100
                    item.setMaximumWeight = 100
                    self.scenelist.addItem(item)

                    endfile = file
            try:
                instex1 = self.projpath + endfile
                # print instex
                jpg1 = QtGui.QPixmap(instex1).scaled(500,500)
                self.label.setPixmap(jpg1)
            except UnboundLocalError:
                pass
        except WindowsError:
            pass

        #connect list items to function
        self.scenelist.doubleClicked.connect(self.openHIP)
        self.scenelist.clicked.connect(self.viewTex)


    def viewTex(self, item):
        texname = item.data()

        instex = self.projpath + texname+".jpg"
        #print instex
        jpg = QtGui.QPixmap(instex).scaled(500,500)
        self.label.setPixmap(jpg)

    def openHIP(self,item):
        filename = item.data()

        hipFile = self.projpath + filename+".hip"
        hou.hipFile.load(hipFile)
        
        #print "author:ARNO"
        #print "QQ:1245527422"