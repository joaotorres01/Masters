import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.*;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;

public class ServidorAdicional extends Servidor{

    Socket socket;
    public ServidorAdicional(String arg) throws IOException, InterruptedException {
        clientesAtivos = new ArrayList<>();
        vizinhos = new ArrayList<>();

        floodSocket = new DatagramSocket(Ports.floodPort);

        helloServer(arg);
        setIP();

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

    public void helloServer(String ip) throws IOException, InterruptedException {
        PrintWriter out;
        BufferedReader in;
        socket = new Socket(ip, Ports.bootstrapPort);
        out = new PrintWriter(socket.getOutputStream(), true);
        out.println("Hello");
        long time = Instant.now().toEpochMilli();
        in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        String line = in.readLine();
        long duration = Instant.now().toEpochMilli() - time;
        out.println("Start");
        Thread.sleep(duration/2);
        System.out.println(Instant.now());
        setupStream();
        setVizinhos(line);
    }

    public void setVizinhos(String line) {
        line = line.substring(1, line.length() - 1);
        String[] ips = line.split(",");
        for (String ip : ips) {
            try {
                InetAddress inetAddress = InetAddress.getByName(ip.trim().replace("/", ""));
                vizinhos.add(inetAddress);
            } catch (UnknownHostException e) {
                e.printStackTrace();
                throw new RuntimeException(e);
            }
        }
        System.out.println("Vizinhos: " + vizinhos);
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
                        ip = addr;
                        System.out.println("My IP: " + ip.getHostAddress());
                    }
                }
            }
        } catch (SocketException e) {
            throw new RuntimeException(e);
        }
    }
}
