/******************************************************************************\
| Copyright (C) 2016 BAP Image Systems                                         |
| All rights reserved                                                          |
| http://www.bapimgsys.com/                                                    |
|==============================================================================|                                                                            
| Mini-camera interface library functions                                      |
\******************************************************************************/


#ifndef _MINICAMERA_INTERFACE_H_
#define _MINICAMERA_INTERFACE_H_

#if defined(WIN32) || defined(_WIN32)
  #ifdef MINICAMERA_MAKING_DLL
    #define MINICAMERA_DLL_EXPORT __declspec (dllexport)
  #else
   #define MINICAMERA_DLL_EXPORT __declspec (dllimport) 
  #endif
#else
  #define MINICAMERA_DLL_EXPORT
#endif



#ifdef __cplusplus
extern "C" {
#endif
 

//refresh the current devices connection status
MINICAMERA_DLL_EXPORT int
minicamera_refresh_device_list (void);

// function to get system version
MINICAMERA_DLL_EXPORT int
minicamera_get_version (
  int device_id,
  unsigned int * version_y,
  unsigned int * version_m,
  unsigned int * version_d,
  unsigned int * version_h,
  unsigned int * version_min,
  unsigned int * version_s,
  unsigned int * version_fpga);

// start grabbing sensor data, after successful calling this function,
// the device application starts to collect data from sensors
MINICAMERA_DLL_EXPORT int
minicamera_start (int device_id);

// stop the device sensor data grab
MINICAMERA_DLL_EXPORT int
minicamera_stop (int device_id);


// get the number of valid frames in the library buffers
// also the size in bytes of the frame
//extern "C"  MINICAMERA_DLL_EXPORT int
MINICAMERA_DLL_EXPORT int
minicamera_get_system_info (
  int device_id,
  unsigned int * valid_frames,
  unsigned int * frame_size);

// the buffer variable must be big enough to fit all frame bytes in all 
// components, worst case scenario is 393216 bytes for 10 bpp in 16 bit words 
// and 3 color components, best case scenario is 61504 for monochromatic frame
// and 8 bits of data in pixel
MINICAMERA_DLL_EXPORT int
minicamera_get_buff (
  int device_id,
  unsigned char * buffer,
  unsigned int * camera_id,
  unsigned int * img_id,
  unsigned int * c_bpp,
  unsigned int * c_num,
  unsigned int * width,
  unsigned int * height,
  unsigned int timeout_ms);

// gets raw image from sensor
// the timeout parameter defines how long (in ms) should the function wait
// for valid frames from sensor, the camera_id parameter returns the camera
// module the frame came from, the img_id parameter returns the number of frame,
// the width and height defines the frame diameters,
// after successful function call the parameters contain:
//
//  buffer - pointer to buffer with image data
//  !! the buffer content is valid till next call of 
//  "minicamera_get_raw_camera_image"
//  camera_id - camera number 0 or 1
//  img_id - image id (incrementing in hardware)
//  c_bpp - component precision in bits per pixel
//  c_num - number of components (3 - RGB, 1 - gray-scale)
//  width - image data width
//  height - image data height
MINICAMERA_DLL_EXPORT int
minicamera_get_raw_camera_image (
  int device_id,
  unsigned char ** buffer,
  unsigned int * camera_id,
  unsigned int * img_id,
  unsigned int * c_bpp,
  unsigned int * c_num,
  unsigned int * width,
  unsigned int * height,
  unsigned int timeout_ms);

//obsolete! This function use is not required any more
MINICAMERA_DLL_EXPORT void
minicamera_free_buffer (unsigned char * buffer);
  
// set led level function to set the less brightness, minimum value - 0
// maximum value 255
// LED_0 and LED_1 are connected to sensor connector 1
// LED_2 and LED_3 are connected to sensor connector 2
#define LED_0 (1 << 0)
#define LED_1 (1 << 1)
#define LED_2 (1 << 2)
#define LED_3 (1 << 3)


MINICAMERA_DLL_EXPORT int
minicamera_set_led_level (
  int device_id,
  unsigned char led_select,
  unsigned char led_value);

// function to start black calibration
MINICAMERA_DLL_EXPORT int
minicamera_perform_calibration (
  int device_id,
  unsigned char camera);

// function to set parameters
// available parameters and parameters values
// are in "minicamera_interface_config.h"
MINICAMERA_DLL_EXPORT int 
minicamera_c_set_parameter (
  int device_id,
  int camera,
  int parameter,
  int value);

MINICAMERA_DLL_EXPORT int 
minicamera_force_disconnect_usb (int device_id);
  




#ifdef __cplusplus
}
#endif

#endif //_MINICAMERA_INTERFACE_H_


