// Không sử dụng using System - phải gọi đầy đủ System.Console
// using System;

// namespace: vùng đặt tên giúp tổ chức mã
namespace HelloWorldApp
{
    // class Program: mọi mã chạy đều nằm trong một lớp
    internal class ProgramWithoutUsing
    {
        // Main: điểm vào chương trình
        static void Main(string[] args)
        {
            // Phải viết đầy đủ System.Console thay vì chỉ Console
            System.Console.WriteLine("Hello World without using System!");

            // Demo phân biệt hoa/thường
            string MyClass = "Uppercase variable";
            string myclass = "Lowercase variable";
            System.Console.WriteLine(MyClass);
            System.Console.WriteLine(myclass);

            // Demo kiểu dữ liệu
            System.Console.WriteLine("\n=== Data Types Demo ===");
            int number = 42;
            double pi = 3.14159;
            bool isStudent = true;
            char grade = 'A';

            System.Console.WriteLine($"Integer: {number}");
            System.Console.WriteLine($"Double: {pi}");
            System.Console.WriteLine($"Boolean: {isStudent}");
            System.Console.WriteLine($"Character: {grade}");

            // Demo args
            System.Console.WriteLine("\n=== Command Line Arguments ===");
            System.Console.WriteLine($"Number of arguments: {args.Length}");
            for (int i = 0; i < args.Length; i++)
            {
                System.Console.WriteLine($"args[{i}] = {args[i]}");
            }

            // Tạm dừng
            System.Console.WriteLine("\nPress ENTER to exit...");
            System.Console.ReadLine();
        }
    }
}