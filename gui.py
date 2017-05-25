#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we select a file with a
QtGui.QFileDialog and display its contents
in a QtGui.QTextEdit.

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

import sys
import PyQt4.QtGui as qt
import PyQt4.QtCore as qtcore
import bdlfiles
import bdlbin
import time
import os
import threading


class BDLGui(qt.QWidget):
    def __init__(self):
        super(BDLGui, self).__init__()

        self.isInit = False
        self.validData = False
        self.lock = threading.Lock()

        self.initUI()
        self.fman = bdlfiles.BDLFileManager()

    def initUI(self):
        self.status = qt.QStatusBar(self)
        #
        # self.timer = qtcore.QTimer(self)
        # self.timer.timeout.connect(self.update_file_table_no_status)
        # self.timer.start(500)

        self.srcle = qt.QLineEdit(self)
        self.srcle.textChanged.connect(self.update_file_table)
        self.srcbtn = qt.QPushButton('Locate SD card', self)
        self.srcbtn.clicked.connect(self.show_src_dialog)

        self.export_loc = ""

        self.export_btn = qt.QPushButton('Export', self)
        self.export_btn.clicked.connect(self.export_files)
        self.clear_btn = qt.QPushButton('Clear all', self)
        self.clear_btn.clicked.connect(self.clear_files)
        self.init_btn = qt.QPushButton('Prepare SD card', self)
        self.init_btn.clicked.connect(self.init_files)

        self.table = qt.QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(['Status', 'File Name'])
        header = self.table.horizontalHeader()
        header.setResizeMode(0, qt.QHeaderView.ResizeToContents)
        header.setResizeMode(1, qt.QHeaderView.Stretch)
        self.table.setColumnWidth(0, 80)

        topBox = qt.QHBoxLayout()
        topBox.addWidget(self.srcbtn)
        topBox.addWidget(self.srcle)
        topBox.addStretch(1)

        bottomBox = qt.QHBoxLayout()
        bottomBox.addStretch(1)
        bottomBox.addWidget(self.init_btn)
        bottomBox.addStretch(1)
        bottomBox.addWidget(self.clear_btn)
        bottomBox.addStretch(1)
        bottomBox.addWidget(self.export_btn)
        bottomBox.addStretch(1)

        mainlayout = qt.QVBoxLayout()
        mainlayout.addLayout(topBox)
        mainlayout.addWidget(self.table)
        mainlayout.addLayout(bottomBox)
        mainlayout.addWidget(self.status)

        self.setLayout(mainlayout)
        self.setGeometry(300, 300, 300, 400)
        self.setWindowTitle('BDL data file converter')
        self.show()

    def show_src_dialog(self):
        if self.isInit:
            return
        fname = qt.QFileDialog.getExistingDirectory(self, 'Select source directory', '/home')
        print(fname)
        if fname is not "":
            self.srcle.setText(fname)
            self.validData = True

    def show_dst_dialog(self):
        if self.isInit:
            return
        fname = qt.QFileDialog.getExistingDirectory(self, 'Select output directory', '/home')
        print(fname)
        if fname is not "":
            self.export_loc = fname

    #
    # def update_file_table_no_status(self):
    #     self.update_file_table(update_status=False)

    def update_file_table(self, text=None, update_status=True):
        if self.isInit:
            return
        if text is None:
            text = self.srcle.displayText()
        self.fman.set_sd_card(text)
        file_status = self.fman.retrieve_file_status()
        print('')
        if len(file_status) is 0:
            self.table.setRowCount(0)
            if update_status:
                self.status.showMessage("Could not find any BDL data files")
            self.validData = False
        else:
            self.table.setRowCount(len(file_status))
            for i in range(len(file_status)):
                self.table.setItem(i, 0, qt.QTableWidgetItem(file_status[i][1]))
                self.table.setItem(i, 1, qt.QTableWidgetItem(file_status[i][0]))
            if update_status:
                self.status.showMessage("Found BDL data files")
            self.validData = True
        return

    def init_files(self):
        if self.isInit:
            return
        msg = qt.QMessageBox()
        msg.setIcon(qt.QMessageBox.Information)
        msg.setWindowTitle('Warning')
        msg.setText('Warning')
        msg.setInformativeText(
            'The process of preparing the SD card can take up to 20 minutes, as it requires creating static data '
            'files.  Make sure the SD card is properly located.  This only needs to be done once.  ')
        msg.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
        ret = msg.exec_()
        if ret == qt.QMessageBox.Cancel:
            return

        self.status.showMessage('Preparing SD card...')
        init_thread = threading.Thread(target=self.fman.initialize_files, kwargs={'lock': self.lock})
        init_thread.start()
        wait_thread = threading.Thread(target=self.wait_on_init)
        wait_thread.start()
        #self.fman.initialize_files()
        #self.update_file_table()

    def wait_on_init(self):
        self.isInit = True
        print('Beginning wait')
        self.lock.acquire()
        print('Done waiting')
        self.lock.release()
        self.isInit = False
        self.status.showMessage('Finished preparing SD card')

    def clear_files(self):
        if self.isInit:
            return
        if not self.validData:
            return
        self.fman.clear_files()
        self.update_file_table()
        self.status.showMessage('Cleared BDL files')

    def export_files(self):
        if self.isInit:
            return
        file_status = self.fman.retrieve_file_status()
        if len(file_status) == 0:
            return
        self.show_dst_dialog()
        timestr = time.strftime('%Y%m%d')
        count = 0
        for i in range(len(file_status)):
            if file_status[i][1] == 'full':
                print("decoding file " + str(i))
                count = count + 1
                dstfile = open(os.path.join(self.export_loc, 'data_' + timestr + '_{0:03d}.csv'.format(i)), 'w')
                srcfile = open(os.path.join(self.fman.sd_root, self.fman.DATAPATH, file_status[i][0]), 'rb')
                bdlbin.main(srcfile, dstfile)
        self.status.showMessage('Exported {0:d} data files to {1:s}'.format(count, self.export_loc))


def main():
    app = qt.QApplication(sys.argv)
    ex = BDLGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
