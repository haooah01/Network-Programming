using System;
using System.Threading.Tasks;

namespace TaskRunApp
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
            Console.WriteLine("Đang lấy dữ liệu bằng Task.Run...");
            string result = Task.Run(async () => await GetDataAsync()).GetAwaiter().GetResult();
            Console.WriteLine($"Kết quả: {result}");
        }
    }
}
