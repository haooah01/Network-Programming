# 🎯 Tutorial Steps - Individual Runnable Examples

Each step of the tutorial has been created as a separate file that you can run independently. Here's how to test each step:

## 📋 How to Run Each Step

To run any specific step, copy the desired step file to replace the main `Program.cs`:

### Step 2: Basic Math Operation
```powershell
Copy-Item "TutorialSteps\Program_Step2_Basic.cs" "Program.cs"
dotnet run
```
**Expected Output**: `161`

### Step 3: Basic Calculator
```powershell
Copy-Item "TutorialSteps\Program_Step3_BasicCalculator.cs" "Program.cs"
dotnet run
```
**Features**: Interactive calculator with integer support

### Step 4: Decimal Support
```powershell
Copy-Item "TutorialSteps\Program_Step4_DecimalSupport.cs" "Program.cs"
dotnet run
```
**Features**: Same as Step 3 but supports decimal numbers

### Step 5: Division by Zero Handling
```powershell
Copy-Item "TutorialSteps\Program_Step5_DivisionByZero.cs" "Program.cs"
dotnet run
```
**Features**: Same as Step 4 but prevents division by zero

### Step 6: Complete OOP Version (Default)
```powershell
# This is already the main Program.cs file
dotnet run
```
**Features**: Full-featured calculator with error handling and validation

## 🔄 Restore Original Version

To go back to the final complete version:
```powershell
git checkout HEAD -- Program.cs
# or manually copy the complete version back
```

## 🧪 Testing Each Version

1. **Step 2**: Tests basic variable assignment and arithmetic
2. **Step 3**: Tests user input and switch statements
3. **Step 4**: Tests decimal number processing
4. **Step 5**: Tests division by zero protection
5. **Step 6**: Tests comprehensive error handling and OOP structure

All versions demonstrate the progressive enhancement of a simple console calculator into a robust application.