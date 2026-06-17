import java.util.Scanner;

/**
 * Runtime I/O support for generated MKotlin programs (Assignment 4).
 *
 * Generated Jasmin code invokes these static methods for the built-in
 * read*/print* functions described in the specification.
 */
public class io {
    private static final Scanner SC = new Scanner(System.in);

    public static int readInt() {
        return Integer.parseInt(SC.nextLine().trim());
    }

    public static float readFloat() {
        return Float.parseFloat(SC.nextLine().trim());
    }

    public static boolean readBool() {
        return Boolean.parseBoolean(SC.nextLine().trim());
    }

    public static String readString() {
        return SC.nextLine();
    }

    public static void printInt(int value) {
        System.out.print(value);
    }

    public static void printFloat(float value) {
        System.out.print(value);
    }

    public static void printBool(boolean value) {
        System.out.print(value);
    }

    public static void printString(String value) {
        System.out.print(value);
    }
}
