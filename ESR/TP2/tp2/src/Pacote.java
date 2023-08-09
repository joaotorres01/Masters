import java.io.*;
import java.net.InetAddress;

public class Pacote implements Serializable{
    InetAddress origem;
    private int saltos;
    private int conteudo;
    private long timestamp;


    public Pacote(byte[] recBytes) {
        try {
            Pacote msg = deserialize(recBytes);
            this.conteudo = msg.getConteudo();
            this.saltos = msg.getSaltos();
            this.timestamp = msg.getTimestamp();
            this.origem = msg.getOrigem();
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    public Pacote(InetAddress servidor,int conteudo){
        this.origem = servidor;
        this.conteudo = conteudo;
    }

    public Pacote(InetAddress origem, int saltos, int conteudo, long timestamp) {
        this.origem = origem;
        this.saltos = saltos;
        this.conteudo = conteudo;
        this.timestamp = timestamp;
        //System.out.println("Ativos: " + ativos);
    }


    public InetAddress getOrigem() {
        return origem;
    }


    public int getSaltos() {
        return saltos;
    }

    public int getConteudo() {
        return conteudo;
    }

    public long getTimestamp() {
        return timestamp;
    }

    byte[] serialize() throws IOException {
        ByteArrayOutputStream bStream = new ByteArrayOutputStream();
        ObjectOutput oo = new ObjectOutputStream(bStream);
        oo.writeObject(this);
        oo.close();
        return bStream.toByteArray();
    }

    public Pacote deserialize(byte[] recBytes) throws IOException, ClassNotFoundException {
        ObjectInputStream iStream = new ObjectInputStream(new ByteArrayInputStream(recBytes));
        Pacote messageClass = (Pacote) iStream.readObject();
        //System.out.println(messageClass);
        iStream.close();
        return messageClass;
    }

    @Override
    public String toString() {
        return "Packet{" +
                "servidor=" + origem +
                ", saltos=" + saltos +
                ", dados=" + conteudo +
                ", timestamp=" + timestamp +
                '}';
    }
}
