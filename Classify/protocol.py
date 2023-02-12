import cv2
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from GUI import Ui_QR_Code
from pyzbar.pyzbar import decode
import os
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QDateTime
import datetime
import pymssql
import serial
from robot_init import robot_init



class SQL_DB:
    server = 'localhost'
    username = 'sa'
    password = 'Huy1999@'
    database = 'DB_manager'
    table_name = 'table_detail'
    def __init__(self):
        self.conn = pymssql.connect(self.server, self.username, self.password, self.database)
        self.cursor = self.conn.cursor()
    def read(self,arr):
        print("Read")
        self.cursor.execute("SELECT Ho_ten, Dia_chi, SDT FROM table_detail WHERE ID = %s;", arr)
        for i in self.cursor:
            return i

    def write(self,arr):
        """Ham ghi du lieu vao database"""
        print("Write")
        self.cursor.execute(
            'INSERT INTO table_dataIN (Ngay_xuat,ID, Don_vi_van_chuyen) VALUES(%s,%s,%s);',
            (datetime.datetime.now(), arr[2], arr[0])
        )
        self.cursor.execute('SELECT * FROM table_dataIN ORDER BY Ngay_xuat;')
        self.conn.commit()
class send_command:
    def __init__(self):
        self.ser, self.conn = self.connect()
    def connect(self):
        try:
            ser = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=115200,
                timeout=0.1)
            return ser,0
        except:
            return None,1

    def send_data(self, th1, th2, th3, th4, th5):
        try:
            msg = "F" + str(th1) + "A" + str(th2) + "B" + str(th3) + "C" + str(th4) + "D" + str(th5) + "EZ"

            self.ser.write(msg.encode())
            self.ser.flushOutput()
            print("Da truyen xong du lieu")
        except:
            pass

    def send_manual(self, th1, th2, th3, th4, th5):
        try:
            msg = "M" + str(th1) + "A" + str(th2) + "B" + str(th3) + "C" + str(th4) + "D" + str(th5) + "E"
            self.ser.write(msg.encode())
            self.ser.flushOutput()
            print("Da truyen xong du lieu")
        except:
            print("Lỗi kết nối")

class MainWindow:

    def __init__(self):
        super().__init__()
        #print(self.status)
        """******Khoi tao cac bien*****"""

        self.pre_QRcode_data = 0
        self.QRcode_data = 0
        self.myData = 0
        self.DB = SQL_DB()
        """Bien dem san pham"""
        self.count = 0
        self.type1 = 0
        self.type2 = 0
        self.type3 = 0
        self.flag_detect = None
        self.flag_data = False
        self.x_cm = 0
        self.y_cm = 0
        self.command = 0
        self.flag_manual = False
        """Khoi tao vi tri robot"""
        self.robot_init = robot_init()
        self.home_x = 22
        self.home_y = 0
        self.home_z = 22.5
        self.home_pulseA, self.home_pulseB, self.home_pulseC = self.robot_init.InvKinematics(self.home_x,self.home_y, self.home_z)
        self.home_th1, self.home_th2, self.home_th3 = self.robot_init.CurrentPos_deg()
        self.type1_pulseA, self.type1_pulseB, self.type1_pulseC = self.robot_init.InvKinematics(2,-22,10)
        self.type2_pulseA, self.type2_pulseB, self.type2_pulseC = self.robot_init.InvKinematics(-10, -24, 10)
        self.type2_th1, self.type2_th2, self.type2_th3 = self.robot_init.CurrentPos_deg()
        self.type3_pulseA, self.type3_pulseB, self.type3_pulseC = self.robot_init.InvKinematics(-22,-24,12)

        """****KHoi tao GUI*****"""
        self.main_win = QMainWindow()
        self.uic = Ui_QR_Code()
        self.uic.setupUi(self.main_win)
        self.uic.stackedWidget.setCurrentWidget(self.uic.Screen_Home)
        self.timer = QTimer()
        self.serial = send_command()
        #print(self.serial)
        self.status(self.serial.conn)
        #self.timer.timeout.connect(self.show_time)
        #self.timer.start()
        self.uic.line_count_type_1.setText('0')
        self.uic.line_count_type_2.setText('0')
        self.uic.line_count_type_3.setText('0')
        self.uic.sum_oder.setText('0')
        self.uic.x_object.setText("None")
        self.uic.y_object.setText("None")
        self.uic.button_start.clicked.connect(lambda: self.control_panel(1))
        self.uic.button_stop.clicked.connect(lambda: self.control_panel(0))
        self.uic.button_exit.clicked.connect(lambda: self.control_panel(2))
        self.uic.Button_home_SQL.clicked.connect(lambda: self.press_btn(0))
        self.uic.Button_home_Data.clicked.connect(lambda: self.press_btn(0))
        self.uic.Button_SQL.clicked.connect(lambda: self.press_btn(1))
        self.uic.Button_datain.clicked.connect(lambda: self.press_btn(2))
        self.uic.Button_manual.clicked.connect(lambda: self.press_btn(3))
        self.uic.Button_home_manual.clicked.connect(lambda:self.press_btn(0))
        """Button for manual mode"""
        self.uic.btn_baseA.clicked.connect(lambda: self.control_manual(0))
        self.uic.btn_base_A.clicked.connect(lambda: self.control_manual(1))
        self.uic.btn_dof1B.clicked.connect(lambda: self.control_manual(2))
        self.uic.btn_dof1_B.clicked.connect(lambda: self.control_manual(3))
        self.uic.btn_dof2C.clicked.connect(lambda: self.control_manual(4))
        self.uic.btn_dof2_C.clicked.connect(lambda: self.control_manual(5))
        self.uic.btn_dof3D.clicked.connect(lambda: self.control_manual(6))
        self.uic.btn_dof3_D.clicked.connect(lambda: self.control_manual(7))
        self.uic.btn_handE.clicked.connect(lambda: self.control_manual(8))
        self.uic.btn_hand_E.clicked.connect(lambda: self.control_manual(9))
        self.uic.Button_manual_calib.clicked.connect(lambda: self.CalibPos())
        self.uic.Button_refresh.clicked.connect(lambda: self.show_dataIN())
        self.show_table()
        self.uic.Button_findID.clicked.connect(lambda: self.findID())
    def status(self,x):
        if x == 0:
            self.uic.txt_status.setText("Đã kết nối thành công")
            self.uic.light_status.setPixmap(QtGui.QPixmap("icon/icon_denxanh.png"))
        else:
            self.uic.txt_status.setText("Kết nối đã bị ngắt, kiểm tra kết nối")
            self.uic.light_status.setPixmap(QtGui.QPixmap("icon/icon_dendo.png"))
    def press_btn(self,btn):
        if btn == 0:
            self.uic.stackedWidget.setCurrentWidget(self.uic.Screen_Home)
            self.flag_manual = False
        if btn == 1:
            self.uic.stackedWidget.setCurrentWidget(self.uic.Screen_SQL)
        if btn == 2:
            self.uic.stackedWidget.setCurrentWidget(self.uic.Screen_DataIN)
        if btn == 3:
            self.flag_manual = True
            self.uic.stackedWidget.setCurrentWidget(self.uic.Screen_Manual)
    def control_manual(self,x):
        if self.flag_manual == True:
            if x == 0:
                self.serial.send_manual(500,0,0,0,0)
            if x == 1:
                self.serial.send_manual(-500,0,0,0,0)
            if x == 2:
                self.serial.send_manual(0, 500, 0, 0, 0)
                #4170 la 90 do
            if x == 3:
                self.serial.send_manual(0, -500, 0, 0,0)
            if x == 4:
                self.serial.send_manual(0, 0, 500, 0, 0)
            if x == 5:
                self.serial.send_manual(0, 0, -500, 0, 0)
            if x == 6:
                self.serial.send_manual(0, 0, 0, 20, 0)
            if x == 7:
                self.serial.send_manual(0, 0, 0, -20, 0)
            if x == 8:
                self.PickObject(self.x_cm,self.y_cm-3,10.5,3)


    def control_panel(self,x):
        if x == 0:
            self.timer.stop()
            self.uic.Camera.clear()
            self.uic.picture.clear()
            self.uic.Frame_manual.clear()
            self.capture.release()
            #cv2.VideoCapture(0).release()
        elif x ==1:
            self.timer.start()
            self.capture = cv2.VideoCapture(2)
            self.capture.set(3, 640)
            self.capture.set(4, 480)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            self.capture.set(cv2.CAP_PROP_EXPOSURE, -7)
            self.timer.setInterval(int(1000 /30))
            self.timer.timeout.connect(self.main_fcn)
        elif x == 2:
            sys.exit()
    def CalibPos(self):
        try:
            x_ca = float(self.uic.x_calib.text())
            y_ca = float(self.uic.y_calib.text())
            z_ca = float(self.uic.z_calib.text())
            #print(x,y,z)
            ca_pulseA, ca_pulseB, ca_pulseC = self.robot_init.InvKinematics(x_ca,y_ca,z_ca)
            self.serial.send_manual((ca_pulseA -self.home_pulseA), (ca_pulseB-self.home_pulseB) , -(ca_pulseC-self.home_pulseC),0,0)
            self.uic.x_current.setText(str(self.home_x))
            self.uic.y_current.setText(str(self.home_y))
            self.uic.z_current.setText(str(self.home_z))
            self.uic.th1_current.setText(str(self.home_th1))
            self.uic.th2_current.setText(str(self.home_th2))
            self.uic.th3_current.setText(str(self.home_th3))
        except:
            self.uic.x_calib.setText("Lỗi rồi, thử lại")

    def PickObject(self,x,y,z,type):
        pick_pulseA, pick_pulseB, pick_pulseC = self.robot_init.InvKinematics(x,y,z)
        th1,th2, th3 = self.robot_init.CurrentPos_deg()
        th1 = int(round(th1,0))
        print (th1)
        self.serial.send_data(self.home_pulseA - pick_pulseA, 0,0, th1-90,0)
        self.serial.send_data(0,-(self.home_pulseB - pick_pulseB), self.home_pulseC - pick_pulseC,0,0)
        self.serial.send_data(0,0,0,0,100)
        self.serial.send_data(0, -(pick_pulseB - self.home_pulseB), pick_pulseC-self.home_pulseC, 90-th1, 0)
        pick_pulseB = self.home_pulseB
        pick_pulseC = self.home_pulseC
        if type ==1:
            self.serial.send_data(pick_pulseA - self.type1_pulseA, -(pick_pulseB - self.type1_pulseB),
                                    (pick_pulseC - self.type1_pulseC), 0,-100)
            print(self.robot_init.CurrentPos_deg())
            self.serial.send_data(0, -(self.type1_pulseB - self.home_pulseB),
                                    self.type1_pulseC - self.home_pulseC, 0, 0)
            self.serial.send_data(self.type1_pulseA - self.home_pulseA, 0, 0, 0, 0)
        if type == 2:
            self.serial.send_manual(pick_pulseA - self.type2_pulseA, -(pick_pulseB - self.type2_pulseB),
                                      (pick_pulseC - self.type2_pulseC), 0, -100)
            print(self.robot_init.CurrentPos_deg())
            self.serial.send_manual(0, -(self.type2_pulseB - self.home_pulseB),
                                      self.type2_pulseC - self.home_pulseC, 0, 0)
            self.serial.send_manual(self.type2_pulseA - self.home_pulseA,0,0,0,0)
        if type == 3:
            self.serial.send_manual(pick_pulseA - self.type3_pulseA, -(pick_pulseB - self.type3_pulseB),
                                    (pick_pulseC - self.type3_pulseC), 0,-100)

            print(self.robot_init.CurrentPos_deg())
            self.serial.send_manual(0, -(self.type3_pulseB - self.home_pulseB),
                                    self.type3_pulseC - self.home_pulseC, 0, 0)
            self.serial.send_manual(self.type3_pulseA - self.home_pulseA, 0, 0, 0, 0)

    def show_table(self):
        self.DB.cursor.execute("SELECT * FROM table_detail")
        for x,data_x in enumerate(self.DB.cursor):
            self.uic.tableWidget.insertRow(x)
            for y, data_y in enumerate(data_x):
                self.uic.tableWidget.setItem(x,y,QTableWidgetItem(str(data_y)))
            #self.uic.tableWidget.insertRow(i)
    def show_dataIN(self):
        self.uic.table_dataIN.clearContents()
        self.DB.cursor.execute("SELECT * FROM table_DataIN")
        for x,data_x in enumerate(self.DB.cursor):
            self.uic.table_dataIN.insertRow(x)
            for y, data_y in enumerate(data_x):
                self.uic.table_dataIN.setItem(x,y,QTableWidgetItem(str(data_y)))
            #self.uic.tableWidget.insertRow(i)
    def findID(self):
        self.uic.txt_dataIN_ID.setStyleSheet("color: rgb(0, 0, 0)")
        ID = self.uic.txt_dataIN_ID.text()
        try:
            info = self.DB.read(ID)
            self.uic.txt_name_dataIN.setText(info[0])
            self.uic.txt_address_dataIN.setText(info[1])
            self.uic.txt_phone_dataIN.setText(info[2])
        except:
            self.uic.txt_dataIN_ID.setStyleSheet("color: rgb(239, 41, 41)")
            self.uic.txt_dataIN_ID.setText("Không tồn tại ID")

    def show_time(self):
        self.uic.date_time.setDateTime(QDateTime.currentDateTime())
        self.uic.date_time.setDisplayFormat("MM/dd/yyyy hh:mm:ss")
    def show_screen(self):
        self.main_win.show()
    def main_fcn(self):
        self.show_time()
        _, frame = self.capture.read()
        belt = frame[0:480, 155:437]
        #QRarea = belt[0:240,0:278]
        #cv2.line(belt, (0, 240), (278, 240), (0, 0, 0), 1)
        #cv2.imshow("belt", belt)

        gray_belt = cv2.cvtColor(belt, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray_belt, 180, 255, cv2.THRESH_BINARY)
        # x = 105, y=3; x = 374 , y = 477
        # Detect the Nuts
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        # contours = contours[0] if imutils.is_cv2() else contours[1]
        for cnt in contours:

            (x, y, w, h) = cv2.boundingRect(cnt)
            """Let (x,y) be the top-left coordinate of the rectangle and (w,h) be its width and height."""

            # Calculate area
            area = cv2.contourArea(cnt)
            if area > 10000:
                #print(self.speed)
                self.flag_detect = True  # co bao da detect duoc vat
                cv2.rectangle(belt, (x, y), (x + w, y + h), (255, 255, 0), 3)
                cv2.putText(belt, str(area), (x, y), 1, 1, (0, 255, 0))
                x_pixel = x + int(w / 2)
                y_pixel = y + int(h / 2)
                cv2.circle(belt, (x_pixel, y_pixel), 4, (0, 0, 255), -1)
                """if x_pixel != self.pre_x_pixel or y_pixel != self.pre_y_pixel:
                    self.pre_x_pixel = x_pixel
                    self.pre_y_pixel = y_pixel"""
                x_cm, y_cm = self.ConvertP2W(x_pixel, y_pixel)
                Coor = np.array([[x_cm],[y_cm],[0],[1]])
                T = self.robot_init.TransferCoor(17.1,3,0,0,0,0)
                Coor = T@Coor
                self.y_cm = Coor[1,0]
                self.x_cm = Coor[0,0]
                self.uic.x_object.setText(str(round(self.x_cm,3))+" cm")
                self.uic.y_object.setText(str(round(self.y_cm,3))+" cm")
                cv2.putText(belt, "center", (x_pixel - 25, y_pixel - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                text = "x: " + str(round(self.x_cm, 2)) + "cm, y: " + str(round(self.y_cm, 2)) + " cm"
                #text2 = "speed: " + str(round(sum_v,3)) + "cm/s"
                #cv2.putText(belt, text2, (x_pixel - 25, y_pixel + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                #cv2.putText(belt, text, (x_pixel - 90, y_pixel + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # cv2.putText(belt,text2 , (x2 + 50, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if self.flag_detect == True:
            self.uic.x_object.setText(str(self.x_cm))
            self.uic.y_object.setText(str(self.y_cm))
            self.flag_detect = False
        else:
            self.uic.x_object.setText("None")
            self.uic.y_object.setText("None")

        for barcode in decode(belt):
                #send_data(1,2,3)
                # print(barcode.data)
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape(-1, 1, 2)
                cv2.polylines(belt, [pts], True, (0, 255, 0), 5)
                self.QRcode_data = barcode.data.decode()
                if self.QRcode_data != self.pre_QRcode_data:
                    self.flag_data = True  # flag_data la co bao co du lieu vao
                    #path = '/QRcode/venv/data'
                    #cv2.imwrite(os.path.join(path, 'opencv' + str(count) + '.png'), belt)
                    self.count = self.count + 1
                    self.uic.sum_oder.setText(str(self.count))
                    self.uic.txt_total_manual.setText(str(self.count))
                    #print("So don hang", self.count)
                    beep = lambda i: os.system("echo -n '\a';sleep 0.2;" * i)
                    beep(1)
                    # print(myData)
                    self.pre_QRcode_data = self.QRcode_data
                    self.myData = self.QRcode_data.split(".")
                    #print("QR ", myData)
                    self.DB.write(self.myData)
                    Information = self.DB.read(self.myData[2])
                    self.uic.line_customer_name.setText(Information[0])
                    self.uic.txt_name_manual.setText(Information[0])
                    self.uic.line_customer_address.setText(Information[1])
                    self.uic.txt_address_manual.setText(Information[1])
                    self.uic.line_customer_phone.setText(Information[2])
                    self.uic.txt_sdt_manual.setText(Information[2])
                    #print(Information)

                else:
                    self.flag_data = False
        scale_percent = 84  # percent of original size
        width = int(belt.shape[1] * scale_percent / 100)
        height = int(belt.shape[0] * scale_percent / 100)
        dim = (width, height)

        # resize image
        belt_resize = cv2.resize(belt, dim, interpolation=cv2.INTER_AREA)
        # cv2.imshow("frame", belt_resize)
        image = QImage(belt_resize, *belt_resize.shape[1::-1], QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(image)
        self.uic.Camera_manual.setPixmap(pixmap)
        self.uic.Camera.setPixmap(pixmap)
        if self.flag_data == True:
                self.flag_data = False
                self.command, database = self.ProcessData(self.myData)
                #self.PickObject(self.x_cm,self.y_cm-3,11.5,self.command)
                self.uic.picture.setPixmap(pixmap)
                self.uic.Frame_manual.setPixmap(pixmap)
        #cv2.imshow("belt", belt)

    def ProcessData(self,data):
        if data[1] == "SGQ1":
            self.type1 = self.type1 + 1
            self.uic.line_count_type_1.setText(str(self.type1))
            self.uic.txt_type1_manual.setText(str(self.type1))
            return 1, data[2]
        elif data[1] == "SGQ2":
            self.type2 = self.type2 + 1
            self.uic.line_count_type_2.setText(str(self.type2))
            self.uic.txt_type2_manual.setText(str(self.type2))
            return 2, data[2]
        else:
            self.type3 = self.type3 + 1
            self.uic.line_count_type_3.setText(str(self.type3))
            self.uic.txt_type3_manual.setText(str(self.type3))
            return 3, data[2]
    """def send_data(self,th1, th2, th3, th4, th5):
            self.client.publish(th1,th2,th3,th4,th5)
            self.client.subscribe()"""

    def ConvertP2W(self,x_pixel,y_pixel):
        """
        d (cm) la kich thuoc cua khung hinh ma camera quan sat duoc ung voi truc pixel y
        y la tong so pixel nam tren truc y
        """
        CM_TO_PIXEL = 15 / 480
        x_cm = x_pixel * CM_TO_PIXEL
        y_cm = y_pixel * CM_TO_PIXEL
        return x_cm, y_cm
if __name__=="__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show_screen()
    sys.exit(app.exec())