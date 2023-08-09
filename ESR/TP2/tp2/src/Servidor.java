/* ------------------
   Servidor
   usage: java Servidor [Video file]
   adaptado dos originais pela equipa docente de ESR (nenhumas garantias)
   colocar primeiro o cliente a correr, porque este dispara logo
   ---------------------- */

import java.io.*;
import java.net.*;
import java.awt.*;
import java.awt.event.*;
import java.sql.Time;
import java.time.Instant;
import java.util.*;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;
import javax.swing.*;
import javax.swing.Timer;


public class Servidor implements ActionListener {
    Map<InetAddress, java.util.List<InetAddress>> mapTopologia; // bootstrapper
    Map<InetAddress, Boolean> actives; // map of active nodes
    ServerSocket serverSocket; // main socket always listening
    DatagramSocket floodSocket; // socket to send flood messages
    DatagramSocket activateSocket; // socket to receive stream's request by clients

    int idFlood = 0; // id of flood message
    ReentrantLock lock = new ReentrantLock();
    InetAddress cliente;
    List<InetAddress> clientesAtivos;
    List<InetAddress> vizinhos;
    InetAddress ip;

    boolean isRunning = false;

    //RTP variables:
    //----------------
    DatagramPacket senddp; //UDP packet containing the video frames (to send)A
    DatagramSocket RTPsocket; //socket to be used to send and receive UDP packet
    //InetAddress ClientIPAddr; //Client IP address

    static String VideoFileName; //video file to request to the server

    //Video constants:
    //------------------
    int imagenb = 0; //image nb of the image currently transmitted
    VideoStream video; //VideoStream object used to access video frames
    static int MJPEG_TYPE = 26; //RTP payload type for MJPEG video
    static int FRAME_PERIOD = 30; //Frame period of the video to stream, in ms
    static int VIDEO_LENGTH = 500; //length of the video in frames

    Timer sTimer; //timer used to send the images at the video frame rate
    byte[] sBuf; //buffer used to store the images to send to the client

    //--------------------------
    //Constructor
    //--------------------------

    public Servidor() {

    }

    public Servidor(String arg) throws IOException {
        java.util.List<java.util.List<InetAddress>> list = parseConfigFile(arg);
        mapTopologia = new HashMap<>();
        actives = new HashMap<>();
        clientesAtivos = new ArrayList<>();
        for (List<InetAddress> l : list) {
            InetAddress ip = l.get(0);
            l.remove(0);
            mapTopologia.put(ip, l);
            actives.put(ip, Boolean.FALSE);
        }
        System.out.println(mapTopologia);
        vizinhos = mapTopologia.get(ip);
        serverSocket = new ServerSocket(Ports.bootstrapPort);
        new Thread(() -> {
            try {
                listen();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }).start();

        floodSocket = new DatagramSocket(Ports.floodPort);

        new Thread(() -> {
            try {
                flood();
            } catch (InterruptedException | IOException e) {
                throw new RuntimeException(e);
            }
        }).start();

        activateSocket = new DatagramSocket(Ports.activatePort);

        new Thread(() -> {
            try {
                listenActivate();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }).start();
    }


    public List<String> getActives() {
        if (actives.isEmpty()) return new ArrayList<>();
        return actives.entrySet().stream().filter(Map.Entry::getValue).map(Map.Entry::getKey).map(InetAddress::getHostAddress).collect(Collectors.toList());
    }


    public void listenActivate() throws IOException {
        DatagramPacket packet = new DatagramPacket(new byte[1024], 1024);
        while (true) {
            activateSocket.receive(packet);
            Pacote p = new Pacote(packet.getData());
            int activate = p.getConteudo();
            if (activate == 1) {
                clientesAtivos.add(p.origem);
                System.out.println("Will start stream to " + packet.getAddress().getHostAddress());
                cliente = packet.getAddress();
                if (!isRunning) {
                    isRunning = true;
                }
            } else if (activate == 0) {
                System.out.println("P Origem: " + p.origem);
                clientesAtivos.remove(p.origem);
                System.out.println("Will stop stream to " + packet.getAddress().getHostAddress());
                if (clientesAtivos.isEmpty()) {
                    stopStream();
                }
            }

        }
    }

    public void sendDeactivate (InetAddress ip) throws IOException {
        Pacote p = new Pacote(ip, 0);
        byte[] buf = p.serialize();
        System.out.println("Sending deactivate of " + ip.getHostAddress());
        for (Map.Entry<InetAddress, Boolean> entry: actives.entrySet()) {
            if(entry.getValue()) {
                System.out.println("Sending deactivate to " + entry.getKey().getHostAddress());
                DatagramPacket packet = new DatagramPacket(buf, buf.length, entry.getKey(), Ports.activatePort);
                activateSocket.send(packet);
            }
        }
        DatagramPacket packet = new DatagramPacket(buf, buf.length, ip, Ports.activatePort);
        activateSocket.send(packet);
    }


    public void flood() throws InterruptedException, IOException {
        while (true) {
            Thread.sleep(200);
            //System.out.println("Actives: " + actives);
            Pacote p = new Pacote(ip, 0, idFlood, Instant.now().toEpochMilli());
            byte[] buf = p.serialize();
            for (InetAddress ip : vizinhos) {
                DatagramPacket packet = new DatagramPacket(buf, buf.length, ip, Ports.floodPort);
                floodSocket.send(packet);
            }
            idFlood++;
        }
    }


    public List<List<InetAddress>> parseConfigFile(String filePath) throws FileNotFoundException, UnknownHostException {
        List<List<InetAddress>> records = new ArrayList<>();
        boolean first = true;
        try (Scanner scanner = new Scanner(new File(filePath));) {
            while (scanner.hasNextLine()) {
                if (first) {
                    first = false;
                    String line = scanner.nextLine();
                    this.ip = InetAddress.getByName(line.trim());
                } else records.add(getRecordFromLine(scanner.nextLine()));
            }
        }
        return records;
    }

    private List<InetAddress> getRecordFromLine(String line) throws UnknownHostException {
        List<InetAddress> values = new ArrayList<>();
        try (Scanner rowScanner = new Scanner(line)) {
            rowScanner.useDelimiter(",");
            while (rowScanner.hasNext()) {
                values.add(InetAddress.getByName(rowScanner.next()));
            }
        }
        return values;
    }

    public void listen() throws IOException {
        while (true) {
            Socket clientSocket = serverSocket.accept();
            InetAddress ip = clientSocket.getInetAddress();
            new Thread(() -> {
                try {
                    BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                    PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                    boolean active = true;
                    while (active) {
                        try {
                            String message = in.readLine();
                            if (message.startsWith("Hello")) {
                                System.out.println("Hello from " + ip);
                                initiateNode(ip);
                                //servidor.addCliente(ip);
                                System.out.println("Mensagem de hello recebida do " + ip);
                                System.out.println("Ativos" + actives);
                                out.println(mapTopologia.get(ip));
                                //setupStream();
                            }
                            if (message.startsWith("Bye")) {
                                terminateNode(ip);
                                //servidor.removeClinete(ip);
                                active = false;
                            }
                            if (message.startsWith("Start")){
                                out.println(Instant.now().plusSeconds(2));
                                Thread.sleep(2);
                                setupStream();
                            }
                        } catch (Exception e) {
                            System.out.println("Connection closed: " + ip);
                            active = false;
                            terminateNode(ip);
                        }
                    }
                } catch (IOException e) {
                    // remove client from list
                    System.out.println("Cliente saiu");
                    throw new RuntimeException(e);
                }
            }).start();
        }
    }

    public void initiateNode(InetAddress ip) {
        try {
            lock.lock();
            actives.put(ip, Boolean.TRUE);
        } finally {
            lock.unlock();
        }
    }

    public boolean isNodeActive(InetAddress ip) {
        try {
            lock.lock();
            return actives.get(ip);
        } finally {
            lock.unlock();
        }
    }

    public void terminateNode(InetAddress ip) throws IOException {
        System.out.println("Terminating node " + ip);
        try {
            lock.lock();
            actives.put(ip, Boolean.FALSE);
        } finally {
            lock.unlock();
        }
        sendDeactivate(ip);
        clientesAtivos.remove(ip);
        if (ip.equals(cliente) || clientesAtivos.isEmpty()) {
            stopStream();
        }
    }

    //------------------------------------
    //main
    //------------------------------------

    public void stopStream() {
        //sTimer.stop();
        isRunning = false;
    }

    public void setupStream() {
        // init para a parte do servidor
        sTimer = new Timer(FRAME_PERIOD, this); //init Timer para servidor
        sTimer.setInitialDelay(0);
        sTimer.setCoalesce(true);
        sBuf = new byte[15000]; //allocate memory for the sending buffer
        VideoFileName = "movie.Mjpeg";
        System.out.println("Servidor: parametro não foi indicado. VideoFileName = " + VideoFileName);
        File f = new File(VideoFileName);
        if (f.exists()) {
            try {
                RTPsocket = new DatagramSocket(); //init RTP socket
                video = new VideoStream(VideoFileName); //init the VideoStream object:
                System.out.println("Servidor: vai enviar video da file " + VideoFileName);

            } catch (SocketException e) {
                System.out.println("Servidor: erro no socket: " + e.getMessage());
            } catch (Exception e) {
                System.out.println("Servidor: erro no video: " + e.getMessage());
            }
        } else {
            System.out.println("Servidor: ficheiro " + VideoFileName + " não existe");
        }
        sTimer.start();
    }

    //------------------------
    //Handler for timer
    //------------------------
    public void actionPerformed(ActionEvent e) {
        //if the current image nb is less than the length of the video
        if (imagenb < VIDEO_LENGTH) {
            //update current imagenb
            imagenb++;
            try {
                //get next frame to send from the video, as well as its size
                int image_length = video.getnextframe(sBuf);

                if(!isRunning) return;

                //Builds an RTPpacket object containing the frame
                RTPpacket rtp_packet = new RTPpacket(MJPEG_TYPE, imagenb, imagenb * FRAME_PERIOD, sBuf, image_length);

                //get to total length of the full rtp packet to send
                int packet_length = rtp_packet.getlength();

                //retrieve the packet bitstream and store it in an array of bytes
                byte[] packet_bits = new byte[packet_length];
                rtp_packet.getpacket(packet_bits);

                //send the packet as a DatagramPacket over the UDP socket
                senddp = new DatagramPacket(packet_bits, packet_length, cliente, Ports.videoPort);
                RTPsocket.send(senddp);

                //System.out.println("Send frame #" + imagenb);
                //print the header bitstream
                //rtp_packet.printheader();

                //update GUI
                //label.setText("Send frame #" + imagenb);
            } catch (Exception ex) {
                System.out.println("Exception caught: " + ex);
                System.exit(0);
            }
        } else {
            //if we have reached the end of the video file, stop the timer

            imagenb = 0;
            try {
                video = new VideoStream(VideoFileName); //init the VideoStream object:
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }

            //sTimer.stop();
        }
    }

}//end of Class Servidor
