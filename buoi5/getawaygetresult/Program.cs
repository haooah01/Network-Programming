using System;
using System.Threading.Tasks;

namespace GetAwaiterGetResultApp
{
    class Program
    {
        static async Task<string> GetDataAsync()
        {
            await Task.Delay(1000); // Giả lập xử lý bất đồng bộ
            return "Kết quả trả về từ GetDataAsync";
        }

        static void Main(string[] args)
        {
            Console.WriteLine("Đang lấy dữ liệu...");
            Task<string> task = GetDataAsync();
            string result = task.GetAwaiter().GetResult();
            Console.WriteLine($"Kết quả: {result}");
        }
    }
}
