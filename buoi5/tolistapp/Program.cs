using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace ToListApp
{
    public class User
    {
        public int id { get; set; }
        public string name { get; set; }
    }

    class Program
    {
        static async Task<User> GetUserAsync(int id)
        {
            // Giả lập truy vấn bất đồng bộ (ví dụ gọi API)
            await Task.Delay(500 + id * 100);
            return new User { id = id, name = $"User{id}" };
        }

        private static async Task ProcessTasksAsTheyCompleteAsync(IEnumerable<int> userIds)
        {
            var getUserTasks = userIds.Select(id => GetUserAsync(id)).ToList();
            while (getUserTasks.Count > 0)
            {
                Task<User> completedTask = await Task.WhenAny(getUserTasks);
                getUserTasks.Remove(completedTask);
                User user = await completedTask;
                Console.WriteLine($"Processed user {user.id} - {user.name}");
            }
        }

        static async Task Main(string[] args)
        {
            var userIds = new List<int> { 1, 2, 3, 4, 5 };
            Console.WriteLine("Processing users as they complete...");
            await ProcessTasksAsTheyCompleteAsync(userIds);
            Console.WriteLine("All users processed.");
        }
    }
}
