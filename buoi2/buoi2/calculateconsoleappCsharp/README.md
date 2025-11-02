# 🚀 C# Console Calculator App Tutorial - Enhanced with Error Handling

This project demonstrates the step-by-step creation of a C# Console Calculator application, enhanced with **Negative/Positive Prompt Analysis** for comprehensive error handling and input validation.

## 🧠 **Negative/Positive Prompt Analysis Applied**

### 🔴 **NEGATIVE PROMPTS** - Issues Identified & Resolved:
- ❌ **Input Validation**: `null`, empty strings, invalid characters, unicode, emojis
- ❌ **Number Format Errors**: Multiple decimals (`1.2.3`), incomplete scientific notation (`1e`)
- ❌ **Mathematical Edge Cases**: Division by zero, overflow, infinity, NaN
- ❌ **Operator Issues**: Case sensitivity, invalid formats, non-English input
- ❌ **System Vulnerabilities**: Memory issues, infinite loops, cultural formatting

### 🟢 **POSITIVE PROMPTS** - Solutions Implemented:
- ✅ **Regex Validation**: `^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$`
- ✅ **Cultural-Aware Parsing**: Handles different decimal separators
- ✅ **Range Validation**: Numbers between 1e-100 and 1e100
- ✅ **Multiple Operator Formats**: `a/add/+`, `s/subtract/-`, etc.
- ✅ **Comprehensive Error Messages**: User-friendly feedback with examples
- ✅ **Graceful Error Recovery**: App continues after errors

## 📁 Project Structure

- **`Program.cs`** - Currently: Error Testing Suite (demonstrating negative prompts)
- **`Program_Demo.cs`** - Enhanced calculator with error handling demonstration
- **`Calculator.csproj`** - .NET 8.0 project file
- **`ERROR_ANALYSIS.md`** - Comprehensive negative/positive prompt analysis
- **`TutorialSteps/`** - Folder containing all tutorial step examples:
  - `Program_Step2_Basic.cs` - Basic math operation (42 + 119)
  - `Program_Step3_BasicCalculator.cs` - Simple calculator with integer support
  - `Program_Step4_DecimalSupport.cs` - Calculator with decimal number support
  - `Program_Step5_DivisionByZero.cs` - Calculator with division by zero handling
  - `README_Steps.md` - Instructions for running individual steps

## 🔄 Tutorial Steps

### Step 1: Create Project
- Target Framework: **.NET 8.0**
- Project Type: **Console Application**

### Step 2: Basic Code (`Program_Step2_Basic.cs`)
Simple addition operation that outputs `161`.

```csharp
int a = 42;
int b = 119;
int c = a + b;
Console.WriteLine(c);
Console.ReadKey();
```

### Step 3: Basic Calculator (`Program_Step3_BasicCalculator.cs`)
Interactive calculator with four basic operations (using integers).

### Step 4: Decimal Support (`Program_Step4_DecimalSupport.cs`)
- Changed `int` → `double`
- Changed `Convert.ToInt32` → `Convert.ToDouble`
- Now supports decimal numbers (e.g., `42.5 / 119.75`)

### Step 5: Division by Zero Handling (`Program_Step5_DivisionByZero.cs`)
Added protection against division by zero with user re-prompt.

### Step 6: Complete OOP Version (`Program.cs`)
Final version with:
- **Calculator class** with static `DoOperation` method
- **Input validation** using `double.TryParse`
- **Error handling** with try-catch blocks
- **Continuous operation** until user chooses to exit
- **Robust error checking** for all edge cases

## ✨ Features of Final Version

✅ **Four basic operations**: Add, Subtract, Multiply, Divide  
✅ **Decimal number support**: Works with floating-point numbers  
✅ **Input validation**: Handles invalid numeric input  
✅ **Division by zero protection**: Prevents math errors  
✅ **Exception handling**: Graceful error recovery  
✅ **Continuous operation**: Keep calculating until user exits  
✅ **User-friendly interface**: Clear prompts and formatting  

## 🚀 How to Run

### Option 1: Test Error Handling (Current)
```powershell
dotnet run
```
**Shows comprehensive testing of all negative prompt scenarios**

### Option 2: Run Enhanced Calculator Demo
```powershell
Copy-Item "Program_Demo.cs" "Program.cs"
dotnet run
```
**Interactive calculator with robust error handling**

### Option 3: Run specific tutorial steps
```powershell
# Example: Test Step 3
Copy-Item "TutorialSteps\Program_Step3_BasicCalculator.cs" "Program.cs"
dotnet run
```

### Option 4: View Error Analysis
Open `ERROR_ANALYSIS.md` for detailed negative/positive prompt documentation.

## 🎯 Sample Usage

```
Console Calculator in C#
------------------------

Type a number, and then press Enter: 42.5
Type another number, and then press Enter: 119.75
Choose an operator from the following list:
	a - Add
	s - Subtract
	m - Multiply
	d - Divide
Your option? d
Your result: 0.35

Press 'n' and Enter to close the app, or press any other key and Enter to continue:
```

## 🔧 Technical Requirements

- **.NET 8.0 SDK**
- **Visual Studio 2022** or **VS Code** with C# extension
- **Windows, macOS, or Linux**

## 📚 Learning Objectives

This tutorial teaches:
- C# console application basics
- Data types (`int` vs `double`)
- User input handling
- Control flow (`switch` statements)
- Object-oriented programming principles
- Exception handling
- Input validation techniques
- Code organization and best practices

---

**🎉 Result**: A fully functional Calculator App in C# Console that supports addition, subtraction, multiplication, division with decimal numbers, input validation, and robust error handling!