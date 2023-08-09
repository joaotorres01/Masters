import java.net.InetAddress;
import java.time.Instant;

public class Metrica implements Comparable<Metrica> {

    private int nrSaltos;
    private long duration_ms;
    private InetAddress address;
    private int nrSequencia;

    public static int range = 50;

    public Metrica(InetAddress address,int nrSaltos, long duration_ms, int nrSequencia) {
        this.address = address;
        this.nrSaltos = nrSaltos;
        this.nrSequencia = nrSequencia;
        this.duration_ms = Instant.now().minusMillis(duration_ms).toEpochMilli();
    }

    @Override
    public int compareTo(Metrica o) {
        if ( duration_ms  > o.getDuration_ms() - range && duration_ms < o.getDuration_ms() + range) {
            if (nrSaltos > o.getNrSaltos()){
                return 1;
            }
            else if (nrSaltos < o.getNrSaltos()){
                return -1;
            }
            else{
                return 0;
            }
        } else if (duration_ms < o.getDuration_ms()) {
            return -1;
        } else {
            return 1;
        }
    }

    public InetAddress getAddress() {
        return address;
    }

    public int getNrSequencia() {
        return nrSequencia;
    }

    public long getDuration_ms() {
        return duration_ms;
    }

    public int getNrSaltos() {
        return nrSaltos;
    }



    @Override
    public String toString() {
        return "Metrica{" +
                "nrSaltos=" + nrSaltos +
                ", duration_ms=" + duration_ms +
                ", address=" + address +
                ", nrSequencia=" + nrSequencia +
                '}';
    }
}
