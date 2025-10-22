using System;
using System.Threading.Tasks;

namespace WaitResultApp
{
    class Program
    {
        static async Task<string> GetDataAsync(bool throwError = false)
        {
            await Task.Delay(1000);
            if (throwError)
                throw new InvalidOperationException("Lỗi khi lấy dữ liệu!");
            return "Kết quả trả về từ GetDataAsync";
        }

        static void Main(string[] args)
        {
            Console.WriteLine("Đang lấy dữ liệu bằng Wait() và Result...");
            Task<string> task = GetDataAsync();
            try
            {
                task.Wait();
                string result = task.Result;
                Console.WriteLine($"Kết quả: {result}");
            }
            catch (AggregateException ex)
            {
                Console.WriteLine($"Lỗi: {ex.InnerException?.Message}");
            }

            // Demo lỗi
            Console.WriteLine("Demo lỗi với Wait() và Result...");
            Task<string> errorTask = GetDataAsync(true);
            try
            {
                errorTask.Wait();
                string errorResult = errorTask.Result;
                Console.WriteLine($"Kết quả: {errorResult}");
            }
            catch (AggregateException ex)
            {
                Console.WriteLine($"Lỗi: {ex.InnerException?.Message}");
            }
        }
    }
}
