/******************************************************************************\
| Copyright (C) 2016 BAP Image Systems                                         |
| All rights reserved                                                          |
| http://www.bapimgsys.com/                                                    |
|==============================================================================|
| Mini-camera interface library configuration                                  | 
| constant defines                                                             |
\******************************************************************************/

#ifndef _MINICAMERA_INTERFACE_CONFIG_H_
#define _MINICAMERA_INTERFACE_CONFIG_H_

#define CAMERA_0  0
#define CAMERA_1  1


// Maximum number of physical mini-camera devices connected at once
#define MC_MAX_DEVICES_NO                      32

//Error codes are returned by the interface functions
#define MC_OK                                    0
#define MC_ERROR_ALREADY_STARTED                -1
#define MC_ERROR_USB_DEVICE_NOT_STARTED         -2
#define MC_ERROR_USB_DEVICE_NOT_PRESENT         -3 
#define MC_ERROR_INDEX_OUT_OF_RANGE             -4
#define MC_ERROR_USB_OPEN                       -5
#define MC_ERROR_USB_COMMUNICATION              -6
#define MC_ERROR_USB_COMMUNICATION_WRITE        -7
#define MC_ERROR_USB_COMMUNICATION_READ         -8
#define MC_ERROR_WRONG_VERSION                  -9
#define MC_NO_IMAGE                            -10

#define MC_OVERFLOW_HW_OFFSET                  -10
// a) Critical overflows between sensor and AC62KUSB hardware:
//   -11 - FPGA overflow from sensor A
//   -12 - FPGA overflow from sensor B
//   -13 - FPGA overflow from both sensors
// b) Overflow of the data queues in the AC62KUSB (USB too slow):
//   -14 - DSP overflow from sensor A
//   -18 - DSP overflow from sensor B
//   -22 - DSP overflow from both sensors
#define MC_OVERFLOW_HW_END                     -25

#define MC_FUNCTION_OBSOLETE                   -30

#define MC_OVERFLOW_SW                         -63



// parameter to enable/disable camera data output
// values :
// 0 - camera disabled
// 1 - camera enabled
#define MINICAMERA_INT_PARAM_CAMERA_ENABLE                  0x1002
// parameter to enable/disable fixed pattern generation in
// hardware, without using sensor input
// values :
// 0 - pattern disabled (data from sensor)
// 1 - pattern enabled
#define MINICAMERA_INT_PARAM_DSP_TEST_PATTERN               0x1005

// sensor exposure time parameter
// values :
// min - 0 (darkest image)
// max - 249 (brightest image)
#define MINICAMERA_INT_PARAM_EXPOSURE_TIME                  0x1010

// sensor adc gain parameter
// values :
// min - 0 (lowest gain)
// max - 3 (highest gain)
#define MINICAMERA_INT_PARAM_GAIN                           0x1011

// sensor adc offset parameter
// values :
// min - 0 (lowest offset)
// max - 3 (highest offset)
#define MINICAMERA_INT_PARAM_OFFSET                         0x1012

// sensor voltage control
// values in 10mV steps
// min - 160 (1.6 V)
// max - 240 (2.4 V)
#define MINICAMERA_INT_PARAM_VOLTAGE                        0x1020


// set to 1 to enable color reconstruction (demosaic) 
// images will be in RGB interleaved format 
// (R1, G1, B1, R2, G2, B2, ...)
// values :
// 0 - grayscale image (1 component)
// 1 - color RGB images (3 components)
#define MINICAMERA_INT_COLOR_SENSOR                         0x8001

// parameter to enable contrast enhancement option
// every frame brightness is stretched (theoretically increases the visual
// quality)
// values :
// 0 - disable
// 1 - enable
#define MINICAMERA_INT_CONTRAST_ENHANCEMENT                 0x8101
// parameter to enable black offset calibration correction
// the black offset is calculated while the calibration function
// without single calibration function run, the black calibration
// process has no effect
// values :
// 0 - disable
// 1 - enable
#define MINICAMERA_INT_BLACK_CALIBRATION                    0x8102



#endif //_MINICAMERA_INTERFACE_CONFIG_H_
