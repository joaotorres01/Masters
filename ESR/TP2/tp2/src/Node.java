import javax.swing.Timer;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.*;
import java.net.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

import static java.lang.Thread.sleep;


// Recebe e também envia pacotes
public class Node implements ActionListener {

    Map<InetAddress, Boolean> vizinhos;
    DatagramSocket floodSocket;
    DatagramSocket activateSocket;
    Map<InetAddress, Set<Integer>> floodSet;
    Map<InetAddress, Map<InetAddress, Metrica>> costMap;
    boolean activate;
    Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> fornecedor = null; //Servidor-Vizinho
    Map<InetAddress, Instant> lastTime;
    Socket socket;
    ReentrantLock costLock = new ReentrantLock();

    //RTP

    //RTP variables:
    //----------------
    DatagramPacket rcvdp; //UDP packet received from the server (to receive)
    DatagramSocket RTPsocket; //socket to be used to send and receive UDP packet

    Timer cTimer; //timer used to receive data from the UDP socket
    byte[] cBuf; //buffer used to store data received from the server


    public Node() throws SocketException {
        vizinhos = new HashMap<>();
        floodSocket = new DatagramSocket(Ports.floodPort);
        activateSocket = new DatagramSocket(Ports.activatePort);

        floodSet = new HashMap<>();
        costMap = new HashMap<>();
        lastTime = new HashMap<>();
        activate = false;
    }

    public Node(String ip) throws IOException {
        vizinhos = new HashMap<>();
        floodSocket = new DatagramSocket(Ports.floodPort);
        activateSocket = new DatagramSocket(Ports.activatePort);


        floodSet = new HashMap<>();
        costMap = new HashMap<>();
        lastTime = new HashMap<>();
        activate = false;

        helloServer(ip);

        try {
            // socket e video
            RTPsocket = new DatagramSocket(Ports.videoPort); //init RTP socket (o mesmo para o cliente e servidor)
            RTPsocket.setSoTimeout(5000); // setimeout to 5s
        } catch (SocketException e) {
            System.out.println("Cliente: erro no socket: " + e.getMessage());
        }

        new Thread(() -> {
            try {
                flood(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();

        new Thread(() -> {
            try {
                listenActivate();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }).start();


        new Thread(() -> {
            try {
                checkBestFornecedor();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }).start();
    }


    public void helloServer(String ip) throws IOException {
        PrintWriter out;
        BufferedReader in;
        socket = new Socket(ip, Ports.bootstrapPort);
        out = new PrintWriter(socket.getOutputStream(), true);
        out.println("Hello");
        in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        String line = in.readLine();
        setVizinhos(line);
    }

    public void setVizinhos(String line) {
        line = line.substring(1, line.length() - 1);
        String[] ips = line.split(",");
        for (String ip : ips) {
            try {
                InetAddress inetAddress = InetAddress.getByName(ip.trim().replace("/", ""));
                vizinhos.put(inetAddress, Boolean.FALSE);
            } catch (UnknownHostException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }
        System.out.println("Vizinhos: " + vizinhos);
    }

    protected void sendActivate(InetAddress servidor, InetAddress fornecedor, int activate) {
        try {
            Pacote p = new Pacote(servidor, activate);
            byte[] buf = p.serialize();
            DatagramPacket packet = new DatagramPacket(buf, buf.length, fornecedor, Ports.activatePort);
            activateSocket.send(packet);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }


    public void checkBestFornecedor() throws InterruptedException {
        while (true) {
            Thread.sleep(500);
            Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> bestFornecedor;
            if (fornecedor == null) continue;
            try {
                bestFornecedor = getBestNeighbor();
            } catch (IOException e) {
                System.out.println("Não há vizinhos");
                continue;
            }
            if (fornecedor == null || !fornecedor.equals(bestFornecedor)) {
                System.out.println("Mudando fornecedor: " + fornecedor + " -> " + bestFornecedor);
                //Deactivate fornecedor
                if (fornecedor != null) sendActivate(fornecedor.getKey(), fornecedor.getValue().getKey(), 0);
                //Activate bestFornecedor
                sendActivate(bestFornecedor.getKey(), bestFornecedor.getValue().getKey(), 1);
                fornecedor = bestFornecedor;
            }
        }
    }


    public void flood(boolean send) throws Exception {
        DatagramPacket packet = new DatagramPacket(new byte[1024], 1024);
        floodSocket.setSoTimeout(2000);
        while (true) {
            try {
                floodSocket.receive(packet);
            } catch (SocketTimeoutException e) {
                System.out.println("Flood timeout");
                fornecedor = null;
                try {
                    costLock.lock();
                    costMap.clear();
                } finally {
                    costLock.unlock();
                }
                continue;
            }
            Pacote msg = new Pacote(packet.getData());
            int nrSequencia = msg.getConteudo();
            long time = msg.getTimestamp();
            int nrHops = msg.getSaltos();
            InetAddress ip = msg.getOrigem();
            lastTime.put(packet.getAddress(), Instant.now());
            lastTime.put(ip, Instant.now());
            Metrica metrica = new Metrica(ip, nrHops, time, nrSequencia);
            try {
                costLock.lock();
                costMap.putIfAbsent(ip, new HashMap<>());
                //costMap.get(ip).put(packet.getAddress(), metrica);
                if (costMap.get(ip).containsKey(packet.getAddress())) {
                    Metrica oldMetrica = costMap.get(ip).get(packet.getAddress());
                    if (oldMetrica.getNrSequencia() >= nrSequencia - 3) {
                        if (metrica.compareTo(oldMetrica) <= 0) {
                            costMap.get(ip).put(packet.getAddress(), metrica);
                        }
                    } else if (oldMetrica.getNrSequencia() < nrSequencia) {
                        System.out.println(metrica.getNrSequencia() + " " + oldMetrica.getNrSequencia());
                        costMap.get(ip).put(packet.getAddress(), metrica);
                    } else {
                        System.out.println("Pacote antigo: " + metrica);
                    }
                } else {
                    costMap.get(ip).put(packet.getAddress(), metrica);
                }
            } finally {
                costLock.unlock();
            }
            if (send) {
                floodSet.putIfAbsent(ip, new HashSet<>());
                if (!floodSet.get(ip).contains(nrSequencia)) {
                    floodSet.get(ip).add(nrSequencia);
                    // send to all neighbors
                    for (Map.Entry<InetAddress, Boolean> vizinho : vizinhos.entrySet()) {
                        if (vizinho.getKey().equals(packet.getAddress())) continue;
                        Pacote p = new Pacote(ip, nrHops + 1, msg.getConteudo(), time);
                        byte[] buf = p.serialize();
                        DatagramPacket packet_1 = new DatagramPacket(buf, buf.length, vizinho.getKey(), Ports.floodPort);
                        try {
                            floodSocket.send(packet_1);
                        } catch (IOException e) {
                            System.out.println("Erro ao enviar pacote para " + vizinho.getKey().getHostAddress());
                        }
                    }
                }
            }
        }
    }

    public void listenActivate() throws IOException {
        DatagramPacket packet = new DatagramPacket(new byte[1024], 1024);
        while (true) {
            activateSocket.receive(packet);
            InetAddress ip = packet.getAddress();
            Pacote p = new Pacote(packet.getData());
            int activate = p.getConteudo();
            if (activate == 1) {
                System.out.println("Receive Activation " + ip);
                vizinhos.put(ip, Boolean.TRUE);
                Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> best = getBestNeighbor();
                if (fornecedor == null) {
                    fornecedor = best;
                    setupStream();
                } else if (best.equals(fornecedor)) continue;
                packet.setAddress(best.getValue().getKey());
                try {
                    activateSocket.send(packet);
                } catch (IOException e) {
                    System.out.println("Activate: Erro ao enviar pacote;");
                }
            } else {
                System.out.println("Receive Deactivation " + ip);
                try {
                    costLock.lock();
                    if (costMap.containsKey(ip)) {
                        ip = p.getOrigem();
                    }
                } finally {
                    costLock.unlock();
                }
                if (vizinhos.containsKey(ip)) {
                    vizinhos.put(ip, Boolean.FALSE);
                    System.out.println("Vizinhos: " + vizinhos);
                    if (!vizinhos.containsValue(Boolean.TRUE) && fornecedor != null) {
                        System.out.println("Não há vizinhos ativos, encerrando stream");
                        packet.setAddress(fornecedor.getValue().getKey());
                        try {
                            activateSocket.send(packet);
                        } catch (IOException e) {
                            System.out.println("Activate: Erro ao enviar pacote;");
                        }
                        stopStream();
                        fornecedor = null;
                    }
                }
            }
        }
    }


    public Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> getBestNeighbor() throws IOException {
        Map<InetAddress, Map.Entry<InetAddress, Metrica>> melhores = new HashMap<>();
        try {
            costLock.lock();
            if (costMap.isEmpty()) throw new IOException("No neighbors");
            //remove metrica if number of sequence is different
            for (Map.Entry<InetAddress, Map<InetAddress, Metrica>> mapEntry : costMap.entrySet()) {
                for (Iterator<Map.Entry<InetAddress, Metrica>> it = mapEntry.getValue().entrySet().iterator(); it.hasNext(); ) {
                    Map.Entry<InetAddress, Metrica> entry = it.next();
                    boolean remove = false;
                    if (lastTime.get(entry.getKey()).isBefore(Instant.now().minusSeconds(1))) {
                        it.remove();
                        remove = true;
                        System.out.println("Removing " + entry.getKey());
                    }
                    if (lastTime.get(mapEntry.getKey()).isBefore(Instant.now().minusSeconds(1))) {
                        if (!remove) it.remove();
                        if (fornecedor != null && fornecedor.getKey().equals(mapEntry.getKey())) {
                            System.out.println("Fornecedor morreu");
                            fornecedor = null;
                        }
                    }
                }
                //System.out.println("-> " +mapEntry.getValue().entrySet().stream().sorted(Map.Entry.comparingByValue()).collect(Collectors.toList()).get(0));
                if (!mapEntry.getValue().isEmpty())
                    melhores.put(mapEntry.getKey(), mapEntry.getValue().entrySet().stream().sorted(Map.Entry.comparingByValue()).collect(Collectors.toList()).get(0));
            }
            //System.out.println("Melhores: " + melhores);
            if (melhores.isEmpty()) throw new IOException("No neighbors");
            Map.Entry<InetAddress, Map.Entry<InetAddress, Metrica>> s = melhores.entrySet().stream().sorted(Map.Entry.comparingByValue(Map.Entry.comparingByValue())).collect(Collectors.toList()).get(0);
            if (fornecedor == null) return s;
            if (s.getValue().getValue().compareTo(fornecedor.getValue().getValue()) < 0) {
                return s;
            } else return fornecedor;
        } finally {
            costLock.unlock();
        }
    }


    private void setupStream() {
        //init para a parte do cliente
        //--------------------------
        cTimer = new Timer(20, this);
        cTimer.setInitialDelay(0);
        cTimer.setCoalesce(true);
        cBuf = new byte[15000]; //allocate enough memory for the buffer used to receive data from the server
        cTimer.start();
    }

    private void stopStream() {
        cTimer.stop();
    }


    public void actionPerformed(ActionEvent e) {

        //Construct a DatagramPacket to receive data from the UDP socket
        rcvdp = new DatagramPacket(cBuf, cBuf.length);

        try {
            //receive the DP from the socket:
            RTPsocket.receive(rcvdp);

            //create an RTPpacket object from the DP
            RTPpacket rtp_packet = new RTPpacket(rcvdp.getData(), rcvdp.getLength());


            //get to total length of the full rtp packet to send
            int packet_length = rtp_packet.getlength();

            //retrieve the packet bitstream and store it in an array of bytes
            byte[] packet_bits = new byte[packet_length];
            rtp_packet.getpacket(packet_bits);

            //send the packet as a DatagramPacket over the UDP socket
            DatagramPacket senddp;
            for (Map.Entry<InetAddress, Boolean> vizinho : vizinhos.entrySet()) {
                if (vizinho.getValue()) {
                    //System.out.println(vizinho.getKey());
                    senddp = new DatagramPacket(packet_bits, packet_length, vizinho.getKey(), Ports.videoPort);
                    RTPsocket.send(senddp);
                }
            }
        } catch (InterruptedIOException iioe) {
            System.out.println("Nothing to read");
        } catch (IOException ioe) {
            System.out.println("Exception caught: " + ioe);
        }

    }


}