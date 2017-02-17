using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Awaiba.Drivers.Grabbers;
using Awaiba.FrameProcessing;
using System.Threading;

namespace NaneyeServer
{
    public enum CAMSTATE {NONE, READY, BUSY};

    public partial class NaneyeConsole : Form
    {
        NanEye2DNanoUSB2Provider provider;
        volatile int framesCaptured = 0;
        volatile int frameCount = -1;
        volatile int frameTotal = 0;
        delegate void PrintHandler(string s);
        public volatile CAMSTATE status = CAMSTATE.NONE;
        public static int CCD_WIDTH = 250;
        public static int CCD_HEIGHT = 250;
        double[] data = new double[CCD_WIDTH * CCD_HEIGHT];
        DateTime exp_start;
        double exp_time;

        public NaneyeConsole()
        {
            /** The bin file location and file is set as:
             *  (Location.Paths.FpgaFilesDirectory + Path.DirectorySeparatorChar + BinFile);
             * * */

            InitializeComponent();

            Awaiba.Drivers.Grabbers.Location.Paths.FpgaFilesDirectory = "";
            provider = new NanEye2DNanoUSB2Provider();
            NaneyeInit();
            addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Camera connected");
            status = CAMSTATE.READY;
            SocketListener.naneye = this;
            new Thread(SocketListener.StartListening).Start();
        }

        public void NaneyeInit()
        {
            Thread.Sleep(100);

            provider.ImageProcessed2 += provider_ImageProcessed;
            provider.Exception += provider_Exception;

            /* NanEye Automatic Exposure Control Configuration
            * 
            * Please follow with the "NanEye - Automatic Exposure Control" PDF that can be found on Awaiba Webpage on the software tab:
            * 
            * For .NET (C# or C++/CLI), please go to "AEC in .NET"*/

            /***In classes of "Cesys Provider DLL": ***/

            ///Value that the algorithm will try to get by changing the sensor exposure and gain
            provider.AutomaticExpControl().TargetGreyValue = 512;

            ///Values used inside the algorithm
            provider.AutomaticExpControl().Hysteresis = 16;
            provider.AutomaticExpControl().StepSize = 8;
            provider.AutomaticExpControl().FrameNumber = 0;

            ///Enable the algorithm (value 0); Disable -> value 1;
            provider.AutomaticExpControl().Enabled = 1;

            ///The ShowROI will show the Region of Interest and the current values of the Gain and Exposure
            provider.AutomaticExpControl().ShowROI = 0;

            ///How to define the region of interest (where the algorithm will calculate the value so that it matches the "Target Grey Value":
            ///topROI: Top Line
            ///bottomROI: Bottom line
            ///LeftROI: Left Column
            ///RightROI: Right Column
            ///The region that is inside this four lines is the region of intereset
            provider.AutomaticExpControl().TopROI = 50;
            provider.AutomaticExpControl().BottomROI = 200;
            provider.AutomaticExpControl().LeftROI = 50;
            provider.AutomaticExpControl().RightROI = 200;

            //To send the value 3 to Offset
            provider.WriteRegister(new NanEyeRegisterPayload(false, 0x02, true, 0, 3));

            //To send the value 2 to Gain
            provider.WriteRegister(new NanEyeRegisterPayload(false, 0x01, true, 0, 2));

            //To send the value 250 to exposure
            provider.WriteRegister(new NanEyeRegisterPayload(false, 0x03, true, 0, 249));

            ////To send the value 1.8 to the digipot
            provider.WriteRegister(new NanEyeRegisterPayload(false, 0x04, true, 0, 2000));

            //            Thread myThread = new Thread(camera_test);
            //            myThread.Start();
            //            myThread.Join();
            //            camera_test();
        }

        private void provider_Exception(object sender, OnExceptionEventArgs e)
        {
            addText("Error:" + e.ex.Message);
        }

        private void provider_ImageProcessed(object sender, OnImageReceivedBitmapEventArgs e)
        {
            framesCaptured++;
            if (frameCount >= e.FrameCount || (e.FrameCount >= 255 && frameCount < 0)) return;
            if (e.FrameCount < 255)
            {
                frameCount = e.FrameCount;
            }
            else
            {
                provider.AutomaticExpControl().FrameNumber = 0;
                frameCount = -1;
            }
            frameTotal++;
            for (int i = 0; i < CCD_HEIGHT * CCD_HEIGHT; i++) data[i] += e.GetImageData.RawData[i];
            double tpass = (DateTime.Now - exp_start).TotalSeconds;
            if(tpass > exp_time && status == CAMSTATE.BUSY)
            {
                status = CAMSTATE.READY;
                provider.StopCapture();
                addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Stop capture");
                SocketListener.SendImage(CCD_WIDTH, CCD_HEIGHT, frameTotal, data);
            }
            addText(String.Format("{0}  I:{1} F:{2} C:{3} L:{4} T:{5}", DateTime.Now.ToString("h:mm:ss.fff"), framesCaptured, e.FrameCount, frameTotal, e.GetImageData.RawData.Length, e.FramesTime));
        }

        public void addText(string s)
        {
            if (logBox.InvokeRequired)
            {
                logBox.Invoke(new PrintHandler(addText), s);
            }
            else
            {
                logBox.AppendText("\r\n" + s);
            }
        }

        public void camera_test()
        {
            Thread.Sleep(1000);
            addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Camera connected");
            provider.StartCapture();
            addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Start capture");
            //            ProcessingWrapper.pr[0].TakeSnapshost().rawImage.Save("image.pgm");
            Thread.Sleep(1000);
            provider.StopCapture();
            addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Stop capture");
        }

        private void NaneyeConsole_FormClosed(object sender, FormClosedEventArgs e)
        {
            SocketListener.StopListening();
            Application.Exit();
        }

        public void setGain(int gain)
        {
            provider.WriteRegister(new NanEyeRegisterPayload(false, 0x01, true, 0, gain));
        }

        public void expose(double exptime)
        {
            status = CAMSTATE.BUSY;
            for (int i = 0; i < CCD_WIDTH * CCD_HEIGHT; i++) data[i] = 0;
            exp_start = DateTime.Now;
            exp_time = exptime;
            frameTotal = 0;
            provider.StartCapture();
            addText(DateTime.Now.ToString("h:mm:ss.fff") + "  Start capture");
        }

        public void cancel()
        {
            exp_time = 0;
        }

        private void logBox_TextChanged(object sender, EventArgs e)
        {
        }
    }
}
