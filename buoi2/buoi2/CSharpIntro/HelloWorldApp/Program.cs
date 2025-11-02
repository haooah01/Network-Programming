// using System cho phép gọi Console trực tiếp, không cần System.Console
using System;

// namespace: vùng đặt tên giúp tổ chức mã
namespace HelloWorldApp
{
    // class Program: mọi mã chạy đều nằm trong một lớp
    internal class Program
    {
        // Main: điểm vào chương trình
        static void Main(string[] args)
        {
            // Câu lệnh; kết thúc bằng dấu chấm phẩy ;
            Console.WriteLine("Hello World!");

            // Thử phân biệt hoa/thường (C# phân biệt chữ hoa-thường)
            string MyClass = "Uppercase variable";
            string myclass = "Lowercase variable";
            Console.WriteLine(MyClass);
            Console.WriteLine(myclass);

            // Nếu bỏ using System ở đầu, bạn phải viết:
            // System.Console.WriteLine("Without using System");

            // Demo about data types and variables
            Console.WriteLine("\n=== Data Types Demo ===");
            int number = 42;
            double pi = 3.14159;
            bool isStudent = true;
            char grade = 'A';

            Console.WriteLine($"Integer: {number}");
            Console.WriteLine($"Double: {pi}");
            Console.WriteLine($"Boolean: {isStudent}");
            Console.WriteLine($"Character: {grade}");

            // Demo about args (command line parameters)
            Console.WriteLine("\n=== Command Line Arguments ===");
            Console.WriteLine($"Number of arguments: {args.Length}");
            for (int i = 0; i < args.Length; i++)
            {
                Console.WriteLine($"args[{i}] = {args[i]}");
            }

            // Additional demos
            Console.WriteLine("\n=== String Operations ===");
            string firstName = "John";
            string lastName = "Doe";
            string fullName = firstName + " " + lastName;
            Console.WriteLine($"Full name: {fullName}");
            Console.WriteLine($"Length: {fullName.Length}");
            Console.WriteLine($"Uppercase: {fullName.ToUpper()}");
            Console.WriteLine($"Lowercase: {fullName.ToLower()}");

            Console.WriteLine("\n=== Math Operations ===");
            int a = 10;
            int b = 3;
            Console.WriteLine($"{a} + {b} = {a + b}");
            Console.WriteLine($"{a} - {b} = {a - b}");
            Console.WriteLine($"{a} * {b} = {a * b}");
            Console.WriteLine($"{a} / {b} = {a / b}");
            Console.WriteLine($"{a} % {b} = {a % b}");

            // Pause to see results when running without debug
            Console.WriteLine("\nPress ENTER to exit...");
            Console.ReadLine();
        }
    }
}
