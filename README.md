# ics_fccActor
*ICS FCC Actor - field center camera*

The vendor only provides Windows API for this tiny camera, so we have a camera server(C#) which is running under Windows OS. And this actor(Python) connects to the camera server through the socket interface to access the camera. This is a video camera, all the frames are added during the exposure time and then save as a FITS file. At current stage this actor supports the following commands: expose, abort, status and setGain.

## NANEYE MODULE
![Naneye sensor](http://www.cmosis.com/assets/images/products/Naneye-with-wires-580-1140x752.jpg)
<http://www.cmosis.com/products/product_detail/naneye_module>

The NanEye 2D sensor provides a true system on chip camera head with fully self timed readout sequencing, AD conversion to 10 bit and bit serial data transmission over LVDS. AWAIBA’s proprietary data interface technology permits cable length’s up to 3m with out any additional components at the distal end. Due to the low energy dissipation on the interface no complicated shielding is required to meet EMC norms. With it’s 250 x 250 pixels at 3um pitch the sensors provide clear and sharp images with outstanding MTF in a very compact size. A frame rate of 44FPS permit synchronization to any type of display. The NanEye sensor provides delay free, smooth video operation resulting in a safe operation and a clear diagnosis. The sensors are connected to minimal diameter cabling solutions. A small lens is assembled to the chip, this option does not increase the total diameter of the sensor, making it the world most compact digital camera. 

## NANEYE USB2 DEMO KIT
![USB2 demo kit](http://www.cmosis.com/assets/images/products/Nano_USB2_1.jpg)
<http://www.cmosis.com/products/product_detail/naneye_usb2_demo_kit>

The base station is the hardware between the camera and the PC and it does the deserialisation of the data stream that comes from the camera. The Windows based Module Viewer is a software tool that is able to capture images from the camera via USB2 and makes image corrections such as offset, gain correction, demosaic color reconstruction, etc. 

## AWAIBA camera software
<http://www.awaiba.com/software/>
