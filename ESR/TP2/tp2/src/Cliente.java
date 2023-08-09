/* ------------------
   Cliente
   usage: java Cliente
   adaptado dos originais pela equipa docente de ESR (nenhumas garantias)
   colocar o cliente primeiro a correr que o servidor dispara logo!
   ---------------------- */

import java.io.*;
import java.net.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.Timer;

public class Cliente extends Node {



    InetAddress myIP;

    //GUI\
    //----

    JFrame f = new JFrame("Cliente de Testes");
    JButton setupButton = new JButton("Setup");
    JButton playButton = new JButton("Play");
    JButton pauseButton = new JButton("Pause");
    JButton tearButton = new JButton("Teardown");
    JPanel mainPanel = new JPanel();
    JPanel buttonPanel = new JPanel();
    JLabel iconLabel = new JLabel();
    ImageIcon icon;


    //RTP variables:
    //----------------
    DatagramPacket rcvdp; //UDP packet received from the server (to receive)
    DatagramSocket RTPsocket; //socket to be used to send and receive UDP packet

    Timer cTimer = null; //timer used to receive data from the UDP socket
    byte[] cBuf; //buffer used to store data received from the server


    //--------------------------
    //Constructor
    //--------------------------
    public Cliente(String ip) throws IOException {

        helloServer(ip);

        new Thread(() -> {
            try {
                flood(false);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();

        new Thread(() -> {
            try {
                activate();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }).start();

        setIP();

        try {
            // socket e video
            RTPsocket = new DatagramSocket(Ports.videoPort); //init RTP socket (o mesmo para o cliente e servidor)
            RTPsocket.setSoTimeout(5000); // setimeout to 5s
        } catch (SocketException e) {
            System.out.println("Cliente: erro no socket: " + e.getMessage());
        }

    }


    public void setIP() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface iface = interfaces.nextElement();
                // filters out 127.0.0.1 and inactive interfaces
                if (iface.isLoopback() || !iface.isUp())
                    continue;

                Enumeration<InetAddress> addresses = iface.getInetAddresses();
                while(addresses.hasMoreElements()) {
                    InetAddress addr = addresses.nextElement();
                    if (addr instanceof Inet4Address) {
                        myIP = addr;
                        System.out.println("My IP: " + myIP.getHostAddress());
                    }
                }
            }
        } catch (SocketException e) {
            throw new RuntimeException(e);
        }
    }




    private void activate() throws InterruptedException {
        while (true) {
            Thread.sleep(200);
            try {
                Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> ip = getBestNeighbor();
                //System.out.println("Best neighbor: " + ip.getKey().getHostAddress() + " " + ip.getValue().getHostAddress());
                if (fornecedor == null){
                    fornecedor = ip;
                    System.out.println("Trying to connect to server...");
                    sendActivate(ip.getKey(),ip.getValue().getKey(),1);
                    System.out.println("Activation send");
                    System.out.println("Activation send " + ip.getKey().getHostAddress());
                    if (cTimer == null) setupStream();
                }
                else if (!fornecedor.equals(ip)){
                    System.out.println("Mudar de fornecedor");
                    System.out.println(fornecedor);
                    System.out.println(ip);
                    // Avisar o fornecedor que quero deixar de receber
                    sendActivate(fornecedor.getKey() ,fornecedor.getValue().getKey(),0);
                    // dizer ao novo fornecedor que quero começar a receber
                    sendActivate(ip.getKey(),ip.getValue().getKey(),1);
                    fornecedor = ip;
                }
            } catch (Exception e) {
                System.out.println("Erro ao obter melhor vizinho");
            }
        }
    }


    private void setupStream() {
        //build GUI
        //--------------------------
        //Frame
        f.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                System.exit(0);
            }
        });
        //Buttons
        buttonPanel.setLayout(new GridLayout(1, 0));
        buttonPanel.add(setupButton);
        buttonPanel.add(playButton);
        buttonPanel.add(pauseButton);
        buttonPanel.add(tearButton);

        // handlers... (so dois)
        playButton.addActionListener(new playButtonListener());
        tearButton.addActionListener(new tearButtonListener());
        pauseButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                cTimer.stop();
                //pauseStream();
            }
        });

        //Image display label
        iconLabel.setIcon(null);

        //frame layout
        mainPanel.setLayout(null);
        mainPanel.add(iconLabel);
        mainPanel.add(buttonPanel);
        iconLabel.setBounds(0, 0, 380, 280);
        buttonPanel.setBounds(0, 280, 380, 50);

        f.getContentPane().add(mainPanel, BorderLayout.CENTER);
        f.setSize(new Dimension(390, 370));
        f.setVisible(true);

        //init para a parte do cliente
        //--------------------------
        cTimer = new Timer(20, new clientTimerListener());
        cTimer.setInitialDelay(0);
        cTimer.setCoalesce(true);
        cBuf = new byte[15000]; //allocate enough memory for the buffer used to receive data from the server


        cTimer.start();
    }

    //-----------------------
    //Handler for Play button
    //-----------------------
    class playButtonListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {

            System.out.println("Play Button pressed !");
            //start the timers ...
            cTimer.start();
        }
    }

    //Handler for tear button
    //-----------------------
    class tearButtonListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {

            System.out.println("Teardown Button pressed !");
            //stop the timer
            cTimer.stop();
            //exit
            System.exit(0);
        }
    }

    //------------------------------------
    //Handler for timer (para cliente)
    //------------------------------------

    class clientTimerListener implements ActionListener {
        public void actionPerformed(ActionEvent e) {

            //Construct a DatagramPacket to receive data from the UDP socket
            rcvdp = new DatagramPacket(cBuf, cBuf.length);

            try {
                //receive the DP from the socket:
                RTPsocket.receive(rcvdp);

                //create an RTPpacket object from the DP
                RTPpacket rtp_packet = new RTPpacket(rcvdp.getData(), rcvdp.getLength());

                //print important header fields of the RTP packet received:
                //System.out.println("Got RTP packet with SeqNum # "+rtp_packet.getsequencenumber()+" TimeStamp "+rtp_packet.gettimestamp()+" ms, of type "+rtp_packet.getpayloadtype());

                //print header bitstream:
                //rtp_packet.printheader();

                //get the payload bitstream from the RTPpacket object
                int payload_length = rtp_packet.getpayload_length();
                byte[] payload = new byte[payload_length];
                rtp_packet.getpayload(payload);

                //get an Image object from the payload bitstream
                Toolkit toolkit = Toolkit.getDefaultToolkit();
                Image image = toolkit.createImage(payload, 0, payload_length);

                //display the image as an ImageIcon object
                icon = new ImageIcon(image);
                iconLabel.setIcon(icon);
            } catch (InterruptedIOException iioe) {
                System.out.println("Nothing to read");
            } catch (IOException ioe) {
                System.out.println("Exception caught: " + ioe);
            }
        }
    }

}//end of Class Cliente

