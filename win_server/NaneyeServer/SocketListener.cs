using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net;
using System.Net.Sockets;

namespace NaneyeServer
{
    class SocketListener
    {
        // Incoming data from the client.
        public static string data = null;
        public static int localPort = 11000;
        public static NaneyeConsole naneye;
        private static Socket listener;
        private static Socket listener2;
        private static Socket handler2 = null;

        public static void StartListening()
        {
            // Data buffer for incoming data.
            byte[] bytes = new Byte[128];

            // Establish the local endpoint for the socket.
            // Dns.GetHostName returns the name of the 
            // host running the application.
            //            IPHostEntry ipHostInfo = Dns.Resolve(Dns.GetHostName());
            //            IPAddress ipAddress = ipHostInfo.AddressList[0];
            IPAddress ipAddress = Array.FindLast(Dns.GetHostEntry(string.Empty).AddressList, a => a.AddressFamily == AddressFamily.InterNetwork);
            IPEndPoint localEndPoint = new IPEndPoint(ipAddress, localPort);
            IPEndPoint localEndPoint2 = new IPEndPoint(ipAddress, localPort + 1);

            // Create a TCP/IP socket.
            listener = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);
            listener2 = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);

            // Bind the socket to the local endpoint and 
            // listen for incoming connections.
            try
            {
                listener.Bind(localEndPoint);
                listener.Listen(10);
                listener2.Bind(localEndPoint2);
                listener2.Listen(10);

                // Start listening for connections.
                while (true)
                {
                    naneye.addText("Waiting for a connection...");
                    // Program is suspended while waiting for an incoming connection.
                    Socket handler = listener.Accept();
                    data = null;
                    naneye.addText("Socket connected");
                    handler2 = listener2.Accept();
                    naneye.addText("Data channel connected");

                    // An incoming connection needs to be processed.
                    while (true)
                    {
                        int bytesRec = handler.Receive(bytes);
                        if (bytesRec <= 0) break;
                        string stringRec = Encoding.ASCII.GetString(bytes, 0, 6).ToUpper();
                        naneye.addText(String.Format(">>>>> {0}, length: {1}", stringRec, bytesRec));
                        if (String.Compare(stringRec, 0, "EXP", 0, 3) == 0)
                        {
                            int exptime = Int32.Parse(stringRec.Substring(3));
                            naneye.addText(String.Format("Start exposing, exposure time={0}s", exptime / 10.0));
                            naneye.expose(exptime / 10.0);
                            handler.Send(Encoding.ASCII.GetBytes("OK\n"));
                        }
                        else if (String.Compare(stringRec, 0, "GAIN", 0, 4) == 0)
                        {
                            int gain = Int32.Parse(stringRec.Substring(4));
                            naneye.setGain(gain);
                            naneye.addText(String.Format("Set gain to {0}", gain));
                            handler.Send(Encoding.ASCII.GetBytes("OK\n"));
                        }
                        else if (String.Compare(stringRec, 0, "CANCEL", 0, 6) == 0)
                        {
                            naneye.cancel();
                            naneye.addText(String.Format("Cancel exposure"));
                            handler.Send(Encoding.ASCII.GetBytes("OK\n"));
                        }
                        else if (String.Compare(stringRec, 0, "STATUS", 0, 6) == 0)
                        {
                            string str = "FL";
                            if(naneye.status == CAMSTATE.NONE)
                            {
                                str = "NC";
                            }
                            else if (naneye.status == CAMSTATE.BUSY)
                            {
                                str = "BU";
                            }
                            else if (naneye.status == CAMSTATE.READY)
                            {
                                str = "RE";
                            }
                            handler.Send(Encoding.ASCII.GetBytes(str + "\n"));
                        }
                        else
                        {
                            handler.Send(Encoding.ASCII.GetBytes("FL\n"));
                        }
                    }
                    // Socket closed
                    naneye.addText("Socket connection closed");

                    handler.Shutdown(SocketShutdown.Both);
                    handler.Close();
                    handler2.Shutdown(SocketShutdown.Both);
                    handler2.Close();
                    handler2 = null;
                }
            }
            catch (Exception e)
            {
                naneye.addText(e.ToString());
            }

            naneye.addText("Exit SocketListener");
        }

        public static void SendImage(int width, int height, int nframes, double[] data)
        {
            // For image transfer
            handler2.Send(BitConverter.GetBytes(width));
            handler2.Send(BitConverter.GetBytes(height));
            handler2.Send(BitConverter.GetBytes(nframes));
            handler2.Send(data.SelectMany(value => BitConverter.GetBytes(value)).ToArray());
        }

        public static void StopListening()
        {
            listener.Close();
            listener2.Close();
        }
    }
}
