
import time
from . import lcdconfig

class LCD_1inch28_Dual(lcdconfig.RaspberryPi):

    width = 240
    height = 240
    def command(self, cmd, left):
        self.digital_write(self.DC_PIN, False)
        self.spi_writebyte([cmd], left)

    def data(self, val, left):
        self.digital_write(self.DC_PIN, True)
        self.spi_writebyte([val], left)

    def reset(self):
        pass
        # """Reset the display"""
        # self.digital_write(self.RST_PIN,True)
        # time.sleep(0.01)
        # self.digital_write(self.RST_PIN,False)
        # time.sleep(0.01)
        # self.digital_write(self.RST_PIN,True)
        # time.sleep(0.01)

    def Init(self, left):
        """Initialize dispaly"""
        self.module_init()
        self.reset()

        self.command(0xEF, left)
        self.command(0xEB, left)
        self.data(0x14, left)

        self.command(0xFE, left)
        self.command(0xEF, left)

        self.command(0xEB, left)
        self.data(0x14, left)

        self.command(0x84, left)
        self.data(0x40, left)

        self.command(0x85, left)
        self.data(0xFF, left)

        self.command(0x86, left)
        self.data(0xFF, left)

        self.command(0x87, left)
        self.data(0xFF, left)

        self.command(0x88, left)
        self.data(0x0A, left)

        self.command(0x89, left)
        self.data(0x21, left)

        self.command(0x8A, left)
        self.data(0x00, left)

        self.command(0x8B, left)
        self.data(0x80, left)

        self.command(0x8C, left)
        self.data(0x01, left)

        self.command(0x8D, left)
        self.data(0x01, left)

        self.command(0x8E, left)
        self.data(0xFF, left)

        self.command(0x8F, left)
        self.data(0xFF, left)


        self.command(0xB6, left)
        self.data(0x00, left)
        self.data(0x20, left)

        self.command(0x36, left)
        self.data(0x08, left)

        self.command(0x3A, left)
        self.data(0x05, left)


        self.command(0x90, left)
        self.data(0x08, left)
        self.data(0x08, left)
        self.data(0x08, left)
        self.data(0x08, left)

        self.command(0xBD, left)
        self.data(0x06, left)

        self.command(0xBC, left)
        self.data(0x00, left)

        self.command(0xFF, left)
        self.data(0x60, left)
        self.data(0x01, left)
        self.data(0x04, left)

        self.command(0xC3, left)
        self.data(0x13, left)
        self.command(0xC4, left)
        self.data(0x13, left)

        self.command(0xC9, left)
        self.data(0x22, left)

        self.command(0xBE, left)
        self.data(0x11, left)

        self.command(0xE1, left)
        self.data(0x10, left)
        self.data(0x0E, left)

        self.command(0xDF, left)
        self.data(0x21, left)
        self.data(0x0c, left)
        self.data(0x02, left)

        self.command(0xF0, left)
        self.data(0x45, left)
        self.data(0x09, left)
        self.data(0x08, left)
        self.data(0x08, left)
        self.data(0x26, left)
        self.data(0x2A, left)

        self.command(0xF1, left)
        self.data(0x43, left)
        self.data(0x70, left)
        self.data(0x72, left)
        self.data(0x36, left)
        self.data(0x37, left)
        self.data(0x6F, left)


        self.command(0xF2, left)
        self.data(0x45, left)
        self.data(0x09, left)
        self.data(0x08, left)
        self.data(0x08, left)
        self.data(0x26, left)
        self.data(0x2A, left)

        self.command(0xF3, left)
        self.data(0x43, left)
        self.data(0x70, left)
        self.data(0x72, left)
        self.data(0x36, left)
        self.data(0x37, left)
        self.data(0x6F, left)

        self.command(0xED, left)
        self.data(0x1B, left)
        self.data(0x0B, left)

        self.command(0xAE, left)
        self.data(0x77, left)

        self.command(0xCD, left)
        self.data(0x63, left)


        self.command(0x70, left)
        self.data(0x07, left)
        self.data(0x07, left)
        self.data(0x04, left)
        self.data(0x0E, left)
        self.data(0x0F, left)
        self.data(0x09, left)
        self.data(0x07, left)
        self.data(0x08, left)
        self.data(0x03, left)

        self.command(0xE8, left)
        self.data(0x34, left)

        self.command(0x62, left)
        self.data(0x18, left)
        self.data(0x0D, left)
        self.data(0x71, left)
        self.data(0xED, left)
        self.data(0x70, left)
        self.data(0x70, left)
        self.data(0x18, left)
        self.data(0x0F, left)
        self.data(0x71, left)
        self.data(0xEF, left)
        self.data(0x70, left)
        self.data(0x70, left)

        self.command(0x63, left)
        self.data(0x18, left)
        self.data(0x11, left)
        self.data(0x71, left)
        self.data(0xF1, left)
        self.data(0x70, left)
        self.data(0x70, left)
        self.data(0x18, left)
        self.data(0x13, left)
        self.data(0x71, left)
        self.data(0xF3, left)
        self.data(0x70, left)
        self.data(0x70, left)

        self.command(0x64, left)
        self.data(0x28, left)
        self.data(0x29, left)
        self.data(0xF1, left)
        self.data(0x01, left)
        self.data(0xF1, left)
        self.data(0x00, left)
        self.data(0x07, left)

        self.command(0x66, left)
        self.data(0x3C, left)
        self.data(0x00, left)
        self.data(0xCD, left)
        self.data(0x67, left)
        self.data(0x45, left)
        self.data(0x45, left)
        self.data(0x10, left)
        self.data(0x00, left)
        self.data(0x00, left)
        self.data(0x00, left)

        self.command(0x67, left)
        self.data(0x00, left)
        self.data(0x3C, left)
        self.data(0x00, left)
        self.data(0x00, left)
        self.data(0x00, left)
        self.data(0x01, left)
        self.data(0x54, left)
        self.data(0x10, left)
        self.data(0x32, left)
        self.data(0x98, left)

        self.command(0x74, left)
        self.data(0x10, left)
        self.data(0x85, left)
        self.data(0x80, left)
        self.data(0x00, left)
        self.data(0x00, left)
        self.data(0x4E, left)
        self.data(0x00, left)

        self.command(0x98, left)
        self.data(0x3e, left)
        self.data(0x07, left)

        self.command(0x35, left)
        self.command(0x21, left)

        self.command(0x11, left)
        time.sleep(0.12)
        self.command(0x29, left)
        time.sleep(0.02)

    def SetWindows(self, Xstart, Ystart, Xend, Yend, left):
        #set the X coordinates
        self.command(0x2A, left)
        self.data(0x00, left)               #Set the horizontal starting point to the high octet
        self.data(Xstart, left)      #Set the horizontal starting point to the low octet
        self.data(0x00, left)               #Set the horizontal end to the high octet
        self.data(Xend - 1, left) #Set the horizontal end to the low octet

        #set the Y coordinates
        self.command(0x2B, left)
        self.data(0x00, left)
        self.data(Ystart, left)
        self.data(0x00, left)
        self.data(Yend - 1, left)

        self.command(0x2C, left)

    def send_buffer(self, buffer, left):
        self.SetWindows ( 0, 0, self.width, self.height, left)
        self.digital_write(self.DC_PIN,True)
        for i in range(0,len(buffer),4096):
            self.spi_writebyte(buffer[i:i+4096], left)

    def ShowImage(self,Image, left):
        """Set buffer to value of Python Imaging Library image."""
        """Write display buffer to physical display"""
        imwidth, imheight = Image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError(f'Image must be same dimensions as display \
                ({self.width}x{self.height}).')
        img = self.np.asarray(Image)
        pix = self.np.zeros((self.width,self.height,2), dtype = self.np.uint8)
        pix[...,[0]] = self.np.add(self.np.bitwise_and(img[...,[0]],0xF8),self.np.right_shift(img[...,[1]],5))
        pix[...,[1]] = self.np.add(self.np.bitwise_and(self.np.left_shift(img[...,[1]],3),0xE0),self.np.right_shift(img[...,[2]],3))
        self.send_buffer(pix.flatten().tolist(), left)
        # self.SetWindows ( 0, 0, self.width, self.height)
        # self.digital_write(self.DC_PIN,True)
        # for i in range(0,len(pix),4096):
        #     self.spi_writebyte(pix[i:i+4096], left)

    def clear(self, left):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height * 2)
        self.send_buffer(_buffer, left)
        # self.SetWindows ( 0, 0, self.width, self.height)
        # self.digital_write(self.DC_PIN,True)
        # for i in range(0,len(_buffer),4096):
        #     self.spi_writebyte(_buffer[i:i+4096], left)


