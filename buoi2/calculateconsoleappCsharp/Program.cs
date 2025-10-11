using System;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Calculator.Demo
{
    class SimpleEnhancedCalculator
    {
        public static double DoOperation(double num1, double num2, string op)
        {
            try
            {
                return op.ToLower().Trim() switch
                {
                    "a" or "add" or "+" => num1 + num2,
                    "s" or "subtract" or "-" => num1 - num2,
                    "m" or "multiply" or "*" => num1 * num2,
                    "d" or "divide" or "/" => num2 != 0 ? num1 / num2 : throw new DivideByZeroException("Cannot divide by zero"),
                    _ => throw new ArgumentException($"Unknown operator: {op}")
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"⚠️ Error: {ex.Message}");
                return double.NaN;
            }
        }

        public static bool TryParseNumber(string? input, out double number)
        {
            number = 0;
            
            if (string.IsNullOrWhiteSpace(input))
            {
                Console.WriteLine("❌ Empty input not allowed");
                return false;
            }

            input = input.Trim();

            // Basic regex validation for number format
            if (!Regex.IsMatch(input, @"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$"))
            {
                Console.WriteLine($"❌ '{input}' contains invalid characters");
                return false;
            }

            if (double.TryParse(input, NumberStyles.Float, CultureInfo.InvariantCulture, out number))
            {
                if (double.IsInfinity(number) || double.IsNaN(number))
                {
                    Console.WriteLine("❌ Infinity/NaN not supported");
                    return false;
                }
                return true;
            }

            Console.WriteLine($"❌ '{input}' is not a valid number");
            return false;
        }

        public static double GetNumber(string prompt)
        {
            while (true)
            {
                Console.Write(prompt);
                if (TryParseNumber(Console.ReadLine(), out double number))
                    return number;
                Console.WriteLine("🔄 Try again...");
            }
        }

        public static string GetOperator()
        {
            while (true)
            {
                Console.WriteLine("Operators: a/add/+, s/subtract/-, m/multiply/*, d/divide//");
                Console.Write("Choose operator: ");
                string? input = Console.ReadLine();
                
                if (string.IsNullOrWhiteSpace(input))
                {
                    Console.WriteLine("❌ Please enter an operator");
                    continue;
                }

                input = input.ToLower().Trim();
                if (input is "a" or "add" or "+" or "s" or "subtract" or "-" or 
                          "m" or "multiply" or "*" or "d" or "divide" or "/")
                {
                    return input;
                }
                Console.WriteLine("❌ Invalid operator, try again");
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            
            Console.WriteLine("🧮 Enhanced Calculator Demo");
            Console.WriteLine("==========================");
            Console.WriteLine("✨ Try these to see error handling:");
            Console.WriteLine("   • Numbers: abc, 1.2.3, empty input");
            Console.WriteLine("   • Operators: xyz, ++, empty input");
            Console.WriteLine("   • Math: divide by zero");
            Console.WriteLine();

            bool continue_ = true;
            int count = 0;

            while (continue_)
            {
                try
                {
                    count++;
                    Console.WriteLine($"🔢 Calculation #{count}");
                    Console.WriteLine("─────────────────");

                    double num1 = SimpleEnhancedCalculator.GetNumber("📥 First number: ");
                    double num2 = SimpleEnhancedCalculator.GetNumber("📥 Second number: ");
                    string op = SimpleEnhancedCalculator.GetOperator();

                    double result = SimpleEnhancedCalculator.DoOperation(num1, num2, op);

                    if (!double.IsNaN(result))
                    {
                        string symbol = op switch
                        {
                            "a" or "add" or "+" => "+",
                            "s" or "subtract" or "-" => "-",
                            "m" or "multiply" or "*" => "×",
                            "d" or "divide" or "/" => "÷",
                            _ => op
                        };
                        Console.WriteLine($"✅ Result: {num1} {symbol} {num2} = {result}");
                    }
                    else
                    {
                        Console.WriteLine("❌ Calculation failed");
                    }

                    Console.WriteLine();
                    Console.Write("Continue? (n to exit): ");
                    if (Console.ReadLine()?.ToLower() == "n")
                        continue_ = false;
                    
                    Console.WriteLine();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"💥 Unexpected error: {ex.Message}");
                }
            }

            Console.WriteLine($"📊 Total calculations: {count}");
            Console.WriteLine("👋 Goodbye!");
        }
    }
}