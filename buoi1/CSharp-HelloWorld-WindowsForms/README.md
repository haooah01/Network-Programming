# HelloWorld Windows Forms Application

A simple Windows Forms application built with C# and .NET Framework 4.7.2.

## Description

This is a basic "Hello World" application that demonstrates:
- Windows Forms GUI development
- Button click event handling
- Label text manipulation
- Basic C# programming concepts

## Features

- **Button Control**: A button with the text "Click this"
- **Label Control**: A label that displays "Hello World!" when the button is clicked
- **Event Handling**: Demonstrates basic event-driven programming

## How to Run

1. Open the solution file `HelloWorld.sln` in Visual Studio
2. Build the project (Build ? Build Solution or Ctrl+Shift+B)
3. Run the application (Debug ? Start Debugging or F5)
4. Click the "Click this" button to see "Hello World!" appear in the label

## Project Structure

```
CSharp-HelloWorld-WindowsForms/
??? HelloWorld.sln              # Solution file
??? HelloWorld/                 # Project folder
    ??? HelloWorld.csproj       # Project file
    ??? Program.cs              # Application entry point
    ??? Form1.cs                # Main form code
    ??? Form1.Designer.cs       # Designer-generated code
    ??? Form1.resx              # Form resources
    ??? App.config              # Application configuration
    ??? Properties/             # Project properties
        ??? AssemblyInfo.cs
        ??? Resources.Designer.cs
        ??? Resources.resx
        ??? Settings.Designer.cs
        ??? Settings.settings
```

## Technical Details

- **Framework**: .NET Framework 4.7.2
- **Language**: C# 7.3
- **Project Type**: Windows Forms Application
- **IDE**: Visual Studio

## Controls

- **btnClickThis**: Button control that triggers the Hello World message
- **lblHelloWorld**: Label control that displays the message

## Event Handlers

- `btnClickThis_Click`: Handles the button click event and updates the label text

## Learning Objectives

This project demonstrates:
1. Creating a Windows Forms application
2. Adding controls to a form
3. Setting control properties (Name, Text, Location, Size)
4. Implementing event handlers
5. Programmatically updating control properties
6. Basic C# syntax and Windows Forms development

Perfect for beginners learning Windows Forms development in C#!