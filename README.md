## Simple Editors
Two simple editors to write and run C++ and C# programs.

Features: Syntax Highlighting, Code Completion

Installation:

For Windows-

1. Download the folder

2. Download Python 2.7.x and add it to PATH

3. Download a C++, C#, Go compiler and add it to PATH

4. Download pygments (pip install pygments)

5. Make a shortcut of Editor.pyw on your desktop

6. Run the program

Optional: You can associate C++ files (and others) with the editor if you like so you can open them when double clicking. You can do it via the terminal. First type "assoc .cpp=cppFile" (you can do this with other extensions too, like .h, and for C# files, .cs, or Go files, .go) and then type "ftype cppFile=PATH_TO_EDITOR.BAT %1 %0" (note: you might need to wrap the path in quotation marks)

Note for C#: If you have .NET installed, you already have the compiler. Search for a "cs.exe".
