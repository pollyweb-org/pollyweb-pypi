
from QR import QR


class HOST_QR(QR):

    def Ephemeral(self):
        qr = self.RequireStr('QR')
        parts = qr.split(',')
        return parts[4]
