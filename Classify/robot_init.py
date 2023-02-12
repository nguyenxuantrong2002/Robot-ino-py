import math
import numpy as np


class robot_init:
    def __init__(self):
        """l1 = 9.4  # so cu 9.3
        l2 = 16  # so cu 16
        l3 = 20  # so cu 19"""
        self.L1 = 9.3 # 9.4
        self.L2 = 16
        self.L3 = 19 # 20
        self.th1 = None
        self.th2 = None
        self.th3 = None
        self.flag = False
    """Tinh dong hoc thuan - nghich robot"""
    def InvKinematics(self, Px, Py, Pz):
        self.flag = True
        L1 = 9.3  # so cu 9.3
        L2 = 16  # so cu 16
        L3 = 19  # so cu 19
        self.th1 = math.atan2(Py,Px)

        c3 = (Px**2 + Py**2 + (Pz - L1)**2 - L2**2 - L3**2)/(2*L2*L3)
        s3 = math.sqrt(1 - c3 * c3)
        self.th3 = math.atan2(s3, c3)
        #print(self.th3)
        Dx = Px*(L3*c3 + L2) + (Pz - L1)*L3*s3*math.cos(self.th1)
        #Dy = L2*(Pz-L1) + L3*((Pz-L1)*c3*cos(self.th1)-Px*s3)#
        Dy = math.cos(self.th1)*(L3*c3+L2)*(Pz - L1) - Px*L3*s3
        #print(Dx,Dy)
        if Px<0:
            self.th2 = -math.pi+math.atan2(Dy, Dx)
        else:
            self.th2 = math.atan2(Dy,Dx)
        print(self.FwKinematics(self.th1,self.th2, self.th3))
        print(self.CurrentPos_deg())
        pulse_A = int(round(16000/360*self.th1*360/(2 * math.pi),0))
        pulse_B = int(round(16000/360*self.th2*360/(2 * math.pi),0))
        pulse_C = int(round(16000/360*self.th3*360/(2 * math.pi),0))
        return pulse_A, pulse_B, pulse_C
    def FwKinematics(self,th1, th2, th3):
        Px = round(math.cos(th1)*(self.L3*math.cos(th2+th3)+self.L2*math.cos(th2)),2)
        Py = round(math.sin(th1)*(self.L3*math.cos(th2+th3)+self.L2*math.cos(th2)),2)
        Pz = round(self.L1 + self.L3*math.sin(th2+th3)+ self.L2*math.sin(th2),2)
        return Px, Py , Pz
    def CurrentPos_deg(self):
        if self.flag == True:
            th1 = round(self.th1*360 / (2 * math.pi), 2)
            th2 = round(self.th2*360 / (2 * math.pi), 2)
            th3 = round(self.th3*360 / (2 * math.pi), 2)
            return th1, th2, th3
        else:
            pass

    def CurrentPos_rad(self):
        if self.flag == True:
            return self.th1, self.th2, self.th3
        else:
            pass

    def TransferCoor(self,dx, dy, dz, theta1, theta2, theta3):
        """
        ***
        T la ma tran tinh tien theo 3 truc x, y, z
        Rx la ma tran quay quanh truc x
        Ry la ma tran quay quanh truc y
        Rz la ma tran quay quanh truc z
        ***
        De tinh duoc toa do cua vat trong he toa do OX1Y1Z1 khi biet toa do cua vat trong he toa do OXYZ
        x1 = T@(ma tran quay theo truc x, y hoac z)@x voi x la toa do cua vat
        """

        T = np.array([[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]])
        Rx = np.array([[1, 0, 0, 0], [0, np.cos(theta1), -np.sin(theta1), 0],
                       [0, np.sin(theta1), np.cos(theta1), 0], [0, 0, 0, 1]])
        Ry = np.array([[np.cos(theta2), 0, np.sin(theta2), 0], [0, 1, 0, 0],
                       [-np.sin(theta2), 0, np.cos(theta2), 0], [0, 0, 0, 1]])
        Rz = np.array([[np.cos(theta3), -np.sin(theta3), 0, 0], [np.sin(theta3), np.cos(theta3), 0, 0],
                       [0, 0, 1, 0], [0, 0, 0, 1]])
        return T @ Rx @ Ry @ Rz