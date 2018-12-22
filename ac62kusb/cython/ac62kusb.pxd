"""AC62kUSB camera library """

cdef extern from 'minicamera_interface_config.h' nogil:

    int CAMERA_0
    int CAMERA_1

# Maximum number of physical mini-camera devices connected at once
    int MC_MAX_DEVICES_NO

# Error codes are returned by the interface functions
    int MC_OK
    int MC_ERROR_ALREADY_STARTED
    int MC_ERROR_USB_DEVICE_NOT_STARTED
    int MC_ERROR_USB_DEVICE_NOT_PRESENT
    int MC_ERROR_INDEX_OUT_OF_RANGE
    int MC_ERROR_USB_OPEN
    int MC_ERROR_USB_COMMUNICATION
    int MC_ERROR_USB_COMMUNICATION_WRITE
    int MC_ERROR_USB_COMMUNICATION_READ
    int MC_ERROR_WRONG_VERSION
    int MC_NO_IMAGE
    int MC_OVERFLOW_HW_OFFSET
    int MC_OVERFLOW_HW_END
    int MC_FUNCTION_OBSOLETE
    int MC_OVERFLOW_SW

# parameter to enable/disable camera data output
# values :
# 0 - camera disabled
# 1 - camera enabled
    unsigned long MINICAMERA_INT_PARAM_CAMERA_ENABLE
# parameter to enable/disable fixed pattern generation in
# hardware, without using sensor input
# values :
# 0 - pattern disabled (data from sensor)
# 1 - pattern enabled
    unsigned long MINICAMERA_INT_PARAM_DSP_TEST_PATTERN

# sensor exposure time parameter
# values :
# min - 0 (darkest image)
# max - 249 (brightest image)
    unsigned long MINICAMERA_INT_PARAM_EXPOSURE_TIME

# sensor adc gain parameter
# values :
# min - 0 (lowest gain)
# max - 3 (highest gain)
    unsigned long MINICAMERA_INT_PARAM_GAIN

# sensor adc offset parameter
# values :
# min - 0 (lowest offset)
# max - 3 (highest offset)
    unsigned long MINICAMERA_INT_PARAM_OFFSET

# sensor voltage control
# values in 10mV steps
# min - 160 (1.6 V)
# max - 240 (2.4 V)
    unsigned long MINICAMERA_INT_PARAM_VOLTAGE

# set to 1 to enable color reconstruction (demosaic) 
# images will be in RGB interleaved format 
# (R1, G1, B1, R2, G2, B2, ...)
# values :
# 0 - grayscale image (1 component)
# 1 - color RGB images (3 components)
    unsigned long MINICAMERA_INT_COLOR_SENSOR

# parameter to enable contrast enhancement option
# every frame brightness is stretched (theoretically increases the visual
# quality)
# values :
# 0 - disable
# 1 - enable
    unsigned long MINICAMERA_INT_CONTRAST_ENHANCEMENT

# parameter to enable black offset calibration correction
# the black offset is calculated while the calibration function
# without single calibration function run, the black calibration
# process has no effect
# values :
# 0 - disable
# 1 - enable
    unsigned long MINICAMERA_INT_BLACK_CALIBRATION


cdef extern from 'minicamera_interface.h' nogil:

#refresh the current devices connection status
    int minicamera_refresh_device_list ()

# function to get system version
    int minicamera_get_version (
        int device_id,
        unsigned int * version_y,
        unsigned int * version_m,
        unsigned int * version_d,
        unsigned int * version_h,
        unsigned int * version_min,
        unsigned int * version_s,
        unsigned int * version_fpga
    )

# start grabbing sensor data, after successful calling this function,
# the device application starts to collect data from sensors
    int minicamera_start (int device_id)

# stop the device sensor data grab
    int minicamera_stop (int device_id)

# get the number of valid frames in the library buffers
# also the size in bytes of the frame
    int minicamera_get_system_info (
        int device_id,
        unsigned int * valid_frames,
        unsigned int * frame_size
    )

# the buffer variable must be big enough to fit all frame bytes in all 
# components, worst case scenario is 393216 bytes for 10 bpp in 16 bit words 
# and 3 color components, best case scenario is 61504 for monochromatic frame
# and 8 bits of data in pixel
    int minicamera_get_buff (
        int device_id,
        unsigned char * buffer,
        unsigned int * camera_id,
        unsigned int * img_id,
        unsigned int * c_bpp,
        unsigned int * c_num,
        unsigned int * width,
        unsigned int * height,
        unsigned int timeout_ms
    )

# gets raw image from sensor
# the timeout parameter defines how long (in ms) should the function wait
# for valid frames from sensor, the camera_id parameter returns the camera
# module the frame came from, the img_id parameter returns the number of frame,
# the width and height defines the frame diameters,
# after successful function call the parameters contain:
#  buffer - pointer to buffer with image data
#  !! the buffer content is valid till next call of 
#  "minicamera_get_raw_camera_image"
#  camera_id - camera number 0 or 1
#  img_id - image id (incrementing in hardware)
#  c_bpp - component precision in bits per pixel
#  c_num - number of components (3 - RGB, 1 - gray-scale)
#  width - image data width
#  height - image data height
    int minicamera_get_raw_camera_image (
        int device_id,
        unsigned char ** buffer,
        unsigned int * camera_id,
        unsigned int * img_id,
        unsigned int * c_bpp,
        unsigned int * c_num,
        unsigned int * width,
        unsigned int * height,
        unsigned int timeout_ms
    )

# obsolete! This function use is not required any more
    void minicamera_free_buffer (unsigned char * buffer)

# set led level function to set the less brightness, minimum value - 0
# maximum value 255
# LED_0 and LED_1 are connected to sensor connector 1
# LED_2 and LED_3 are connected to sensor connector 2
    unsigned char LED_0
    unsigned char LED_1
    unsigned char LED_2
    unsigned char LED_3

    int minicamera_set_led_level (
        int device_id,
        unsigned char led_select,
        unsigned char led_value
    )

# function to start black calibration
    int minicamera_perform_calibration (
        int device_id,
        unsigned char camera
    )

# function to set parameters
# available parameters and parameters values
# are in "minicamera_interface_config.h"
    int minicamera_c_set_parameter (
        int device_id,
        int camera,
        int parameter,
        int value
    )

    int minicamera_force_disconnect_usb (int device_id)

cdef:
    int MC_IMAGE_CAPTURE_TIMEOUT = 200
    int MC_SENSOR_VOLTAGE = 240