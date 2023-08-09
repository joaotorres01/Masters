import java.io.IOException;

public class Main {
    public static void main(String[] args) throws IOException, InterruptedException {

        if ( args.length != 2 ) {
            System.out.println("Usage: java -jar tp2.jar <tipo> <argumento>");
            System.exit(1);
        }
        if (args[0].equals("-S")) {
            Servidor s = new Servidor(args[1]);
        }

        if (args[0].equals("-S2")) {
            ServidorAdicional s = new ServidorAdicional(args[1]);
        }


        if (args[0].equals("-N")){
            //Cliente c = new Cliente();
            Node node = new Node(args[1]);
            //node.listen();
        }
        if (args[0].equals("-C")){
            Cliente c = new Cliente(args[1]);

        }

    }
}