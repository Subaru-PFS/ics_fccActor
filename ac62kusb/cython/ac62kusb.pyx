"""AC62KUSB camera module"""

from cython.view cimport array
import numpy as np
import time
import logging

class Camera:
    """FLI usb camera"""

    def __init__(self, exptime=240, gain=0):
        """search and find the camera device"""

        if type(exptime) is not int or exptime > 249 or exptime < 0:
            raise ValueError(f'Exposure time is out of range(0-249): {exptime}')
        if type(gain) is not int or gain > 3 or gain < 0:
            raise ValueError(f'Gain value is out of range(0-3): {gain}')

        self.device = -1
        self.gain = gain
        self.exptime = exptime
        self.logger = logging.getLogger('ac62kusb')

        for device in range(MC_MAX_DEVICES_NO):
            res = minicamera_get_version(device, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
            if res != MC_OK:
                if res == MC_ERROR_WRONG_VERSION:
                    raise RuntimeError('It is required to update the device before capturing video.')
                continue
            # found a device
            self.device = device
            self.logger.info(f'Found a valid device: {device}')
            break

        if self.device < 0:
            raise RuntimeError('Cannot find any compatible device.')

        # initialization, check pxd file for definition
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_CAMERA_ENABLE, 1)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_DSP_TEST_PATTERN, 0)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_VOLTAGE, MC_SENSOR_VOLTAGE)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_COLOR_SENSOR, 0)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_CONTRAST_ENHANCEMENT, 0)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_EXPOSURE_TIME, self.exptime)
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_GAIN, self.gain)
        minicamera_c_set_parameter(self.device, CAMERA_1, MINICAMERA_INT_PARAM_CAMERA_ENABLE, 0)

        self.logger.info('Camera initialized')

    def setExptime(self, exptime):
        """Set the exposure time in ms(0-249)"""

#        if type(exptime) is not int or exptime > 249 or exptime < 0:
        if exptime > 249 or exptime < 0:
            raise ValueError(f'Exposure time is out of range(0-249): {exptime}')
        self.exptime = exptime
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_EXPOSURE_TIME, self.exptime)
        self.logger.info(f'set exposure time to {exptime}ms')

    def setGain(self, gain):
        """Set the gain(0-3)"""

        if gain > 3 or gain < 0:
            raise ValueError(f'Gain value is out of range(0-3): {gain}')
        self.gain = gain
        minicamera_c_set_parameter(self.device, CAMERA_0, MINICAMERA_INT_PARAM_GAIN, self.gain)
        self.logger.info(f'set gain to {gain}')

    def expose(self, frames=1):
        """Do exposure and return the image"""

        cdef unsigned int camera_id, img_id, width, height, c_bpp, c_num
        cdef unsigned char *buffer = NULL
        cdef unsigned char[:, ::1] mv

        if frames < 0:
            raise ValueError(f'frames value is invalid: {frames}')

        if MC_OK != minicamera_start(self.device):
            raise RuntimeError('failed to start the camera')

        count = 0
        failure = 0
        while count < frames:
            res = minicamera_get_raw_camera_image(self.device, &buffer, &camera_id, &img_id, &c_bpp,
                &c_num, &width, &height, MC_IMAGE_CAPTURE_TIMEOUT)
            if res == MC_OVERFLOW_SW:
                raise RuntimeError('failed to capture images, SW overflow!')
            elif res != MC_OK:
                # It's necessary to skip tons of MC_NO_IMAGE errors in the beginning......
                if res != MC_NO_IMAGE:
                    self.logger.info(f'failed to capture images: {res}, count: {failure}')
                failure += 1
                continue

            self.logger.info(f'capture images successfully, frame:{img_id}, size:{width}x{height}, bpp:{c_bpp}')
            if count == 0:
                self.buffer = np.zeros((height, width), dtype=np.int16)
                self.tstart = time.time()
                self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.tstart))

            mv = <unsigned char[:height, :width]> buffer
            self.buffer += np.asarray(mv)
            count += 1

        minicamera_stop(self.device)