# C# Introduction Project

This project demonstrates the fundamental structure of C# programs and provides complete examples for learning.

## Project Structure

```
CSharpIntro/
├── CSharpIntro.sln                    # Solution file
├── HelloWorldApp/                     # Main console application
│   ├── HelloWorldApp.csproj          # Project file with .NET 8.0 target
│   ├── Program.cs                     # Main program with full C# structure
│   └── ProgramWithoutUsing.cs         # Demo showing difference without 'using System'
├── MiniNet/                           # Mini networking demo
│   ├── MiniNet.csproj                 # Networking project file
│   └── Program.cs                     # HTTP client demo
├── .vscode/
│   └── launch.json                    # VS Code debug configuration
└── README.md                          # This file
```

## Key C# Concepts Demonstrated

### 1. Program Structure
- **using System**: Allows direct use of Console instead of System.Console
- **namespace**: Organizes code and prevents naming conflicts
- **class Program**: All executable code must be in a class
- **static void Main(string[] args)**: Entry point of the program
- **Console.WriteLine()**: Outputs text to console

### 2. Data Types
```csharp
int number = 42;        // Integer
double pi = 3.14159;    // Floating point
bool isStudent = true;  // Boolean
char grade = 'A';       // Character
string name = "John";   // String
```

### 3. Case Sensitivity
C# is case-sensitive:
```csharp
string MyClass = "Uppercase variable";  // Different variable
string myclass = "Lowercase variable";  // from this one
```

### 4. Command Line Arguments
The `args` parameter contains command line arguments:
```csharp
static void Main(string[] args)
{
    Console.WriteLine($"Number of arguments: {args.Length}");
    for (int i = 0; i < args.Length; i++)
    {
        Console.WriteLine($"args[{i}] = {args[i]}");
    }
}
```

## How to Run

### Prerequisites
- .NET SDK 8.0 or later
- VS Code with C# extension (optional for debugging)

### Command Line Usage

1. **Build the solution:**
   ```bash
   dotnet build CSharpIntro.sln
   ```

2. **Run the main application:**
   ```bash
   cd HelloWorldApp
   dotnet run
   ```

3. **Run with command line arguments:**
   ```bash
   dotnet run "param1" "param2" "test argument"
   ```

4. **Run the networking demo:**
   ```bash
   cd MiniNet
   dotnet run
   ```

### VS Code Debugging

1. Open the `CSharpIntro` folder in VS Code
2. Install the C# extension
3. Press F5 to start debugging
4. Choose between:
   - ".NET Launch (Console)" - runs with sample arguments
   - ".NET Launch (No Args)" - runs without arguments

## Sample Output

When running `dotnet run "param1" "param2" "test argument"`:

```
Hello World!
Uppercase variable
Lowercase variable

=== Data Types Demo ===
Integer: 42
Double: 3.14159
Boolean: True
Character: A

=== Command Line Arguments ===
Number of arguments: 3
args[0] = param1
args[1] = param2
args[2] = test argument

=== String Operations ===
Full name: John Doe
Length: 8
Uppercase: JOHN DOE
Lowercase: john doe

=== Math Operations ===
10 + 3 = 13
10 - 3 = 7
10 * 3 = 30
10 / 3 = 3
10 % 3 = 1

Press ENTER to exit...
```

## Files Explanation

### HelloWorldApp.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
```

### Program.cs vs ProgramWithoutUsing.cs
- **Program.cs**: Uses `using System;` → can write `Console.WriteLine()`
- **ProgramWithoutUsing.cs**: No using statement → must write `System.Console.WriteLine()`

## Learning Path

1. **Start with HelloWorldApp** - Learn basic C# structure
2. **Experiment with ProgramWithoutUsing.cs** - Understand the role of `using`
3. **Try MiniNet** - Introduction to networking concepts
4. **Use VS Code debugging** - Learn to set breakpoints and step through code

## Next Steps

This foundation prepares you for:
- Object-Oriented Programming concepts
- Network Programming (TCP/UDP)
- Advanced C# features
- .NET ecosystem exploration

## Common Issues

1. **Build errors**: Ensure .NET 8.0 SDK is installed
2. **Permission errors**: Run VS Code as administrator if needed
3. **Encoding issues**: Use English text to avoid character encoding problems
4. **Missing references**: Restore packages with `dotnet restore`