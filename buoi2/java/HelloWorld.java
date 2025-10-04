/**
 * HelloWorld Java Application
 * Simple Hello World program in Java
 * Created for Network Programming course
 */
public class HelloWorld {
    
    /**
     * Main method - entry point of the application
     * @param args command line arguments
     */
    public static void main(String[] args) {
        // Display welcome messages
        System.out.println("Hello, World!");
        System.out.println("Chao mung den voi lap trinh Java!");
        System.out.println("========================================");
        
        // Display Java information
        System.out.println("Java Version: " + System.getProperty("java.version"));
        System.out.println("Java Vendor: " + System.getProperty("java.vendor"));
        System.out.println("OS Name: " + System.getProperty("os.name"));
        System.out.println("OS Version: " + System.getProperty("os.version"));
        System.out.println("User Name: " + System.getProperty("user.name"));
        System.out.println("========================================");
        
        // Simple interaction
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        System.out.print("Nhap ten cua ban: ");
        String name = scanner.nextLine();
        
        System.out.println("Xin chao, " + name + "!");
        System.out.println("Chuc mung ban da chay thanh cong chuong trinh Java!");
        
        // Display some basic calculations
        System.out.println();
        System.out.println("--- Demo tinh toan don gian ---");
        int a = 10, b = 5;
        System.out.println(a + " + " + b + " = " + (a + b));
        System.out.println(a + " - " + b + " = " + (a - b));
        System.out.println(a + " * " + b + " = " + (a * b));
        System.out.println(a + " / " + b + " = " + (a / b));
        
        scanner.close();
    }
}