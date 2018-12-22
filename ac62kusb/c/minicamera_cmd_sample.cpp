/******************************************************************************\
| Copyright (C) 2017 BAP Image Systems                                         |
| All rights reserved                                                          |
| http://www.bapimgsys.com/                                                    |
|==============================================================================|
| AC62KUSB mini-camera usage example                                           |
| Multi-platform command line application                                      |
\******************************************************************************/


#if defined(WIN32) || defined(_WIN32)
  #pragma warning(push, 0)
#endif
#include <stdio.h>
#if defined(WIN32) || defined(_WIN32)
  #pragma warning(pop)
#endif

#include "bap_system.h" // interplatform console/keyboard functionality
#include "minicamera_interface.h"
#include "minicamera_interface_config.h"


#define TEST_PATTERN_ENABLE 1
#define SENSOR_VOLTAGE 240 // (in 10 mV steps)
#define COLOR_CAPTURE 0 // reconstruct color from Bayer matrix sensor variant
#define CONTRAST_ENHANCEMENT 0
#define IMAGE_CAPTURE_TIMEOUT 200


// check for existence, set up some parameters and start device capture process
static int device_check_and_start (int device)
{
  unsigned int
    y, m, d, h; // firmware version details
  int 
    result,
    camera_id;

  result = minicamera_get_version (device, &y, &m, &d, &h, NULL, NULL, NULL);    
  if (result != MC_OK)
  {
    if (result == MC_ERROR_WRONG_VERSION)
    {
      printf (
        "  Detected device: %d is not updated to proper revision.\n", device);
      printf ("  It's required to update the device before capturing video.\n");
      printf ("  Version in hardware: %04u-%02u-%02u.%02u\n", y, m, d, h);
    }
    return 0;
  }
  printf ("  Found valid device: %d. ", device);
  printf ("Version: %04u-%02u-%02u.%02u\n", y, m, d, h);

  for (camera_id = CAMERA_0; camera_id <= CAMERA_1; camera_id++)
  {
    minicamera_c_set_parameter (
      device,
      camera_id,
      MINICAMERA_INT_PARAM_CAMERA_ENABLE,
      1);
    minicamera_c_set_parameter (
      device,
      camera_id,
      MINICAMERA_INT_PARAM_DSP_TEST_PATTERN,
      TEST_PATTERN_ENABLE);    
    minicamera_c_set_parameter (
      device,
      camera_id,
      MINICAMERA_INT_PARAM_VOLTAGE,
      SENSOR_VOLTAGE);
    minicamera_c_set_parameter (
      device, 
      camera_id, 
      MINICAMERA_INT_COLOR_SENSOR,
      COLOR_CAPTURE);
    minicamera_c_set_parameter (
      device, 
      camera_id, 
      MINICAMERA_INT_CONTRAST_ENHANCEMENT,
      CONTRAST_ENHANCEMENT);    
  }

  if (MC_OK == minicamera_start (device) )
  {
    return 1;
  }

  printf ("Unable to start device: %d.\n", device);
  return 0;
}


// -----------------------------------------------------------------------------
int main ()
{
  unsigned char
    * buffer = NULL;
  unsigned int
    captured_frames = 0,
    time_start,
    time_delta;
  int
    result,
    device,
    valid_devices_no = 0,
    valid_device_map [MC_MAX_DEVICES_NO];  

  console_interactive_enter ();
  while (console_is_key_hit () )
  {
    console_getch ();
  }

  printf ("AC62KUSB mini-camera interface sample. Enumerating devices.\n");
  printf ("--------------------------------------------------------------\n");
 

  for (device = 0; device < MC_MAX_DEVICES_NO; device++)
  {
    valid_device_map [device] = device_check_and_start (device);
    valid_devices_no += valid_device_map [device];
  }


  if (!valid_devices_no)
  {
    printf ("\n");
    printf ("--------------------------------------------------------------\n");
    printf ("Cannot find any compatible device.\n");
    printf ("Please connect updated mini-camera and restart the application.\n");
    printf ("Make sure that udev rules allow user device access if in Linux.\n");    
    console_interactive_leave ();
    return 1;
  }
  
  printf ("--------------------------------------------------------------\n");  
  printf ("Capturing frames: press any key to break...\n");

  time_start = get_time_ms ();

  do
  {
    for (device = 0; device < MC_MAX_DEVICES_NO; device++)
    {
      unsigned int
        camera_id,
        img_id,
        width,
        height;

      if (valid_device_map [device] == 0)
      {
        continue;
      }

      result = minicamera_get_raw_camera_image (
        device,
        &buffer,
        &camera_id,
        &img_id,
        NULL,
        NULL,
        &width,
        &height,
        IMAGE_CAPTURE_TIMEOUT);

      if (result != MC_OK && 
          result != MC_OVERFLOW_SW &&
          (result >= MC_OVERFLOW_HW_OFFSET || result < MC_OVERFLOW_HW_END) )
      {
        continue;
      }
      captured_frames ++;
      printf ("  d: %d, c: %d i: %4d, px: %d x %d, %s: %d\n", 
        device, camera_id, img_id, width, height,
        result != MC_OK ? "overflow" : "OK",
        result);
    }
  } while (!console_is_key_hit () );

  time_delta = get_time_ms () - time_start;
  printf ("Captured %d frames in %d seconds, avg FPS: %d\n",
    captured_frames,
    (time_delta + 500) / 1000, 
    (captured_frames * 1000 + (time_delta >> 1) ) / time_delta);

  // cleanup
  for (int i = 0; i< MC_MAX_DEVICES_NO; i++)
  {
    if (valid_device_map [i] == 0)
    {
      continue;
    }
    minicamera_stop (i);
  }

  while (console_is_key_hit () )
  {
    console_getch ();
  }

  printf ("Finished. Press any key to exit...\n");
  while (!console_is_key_hit () ) {; }
  console_getch ();
  console_interactive_leave ();
  return 0;
}
