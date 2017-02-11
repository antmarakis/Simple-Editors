from Tkinter import *;
import tkFileDialog;
from subprocess import call;
from pygments import lex;
from pygments.lexers import CppLexer;
from Trie import *;
import os.path;
import sys;


noEnter = False;
selecting = False;
word = ""; #Current word
filePath = ""; #The file path of current file
types = [("C++","*.cpp"),("C++","*.hxx"),("C++","*.cc")
        ,("C++ Header","*.h"),("C++ Header","*.hpp"),("C++ Header","*.hxx")];
varChars = {}; #holds the acceptable characters for variable names
variables = []; #variable names used in program


def TagConfig():
    #Keyword colors
    textPad.tag_config("Token.Keyword",foreground="medium blue");
    textPad.tag_config("Token.Keyword.Type",foreground="dark violet");
    textPad.tag_config("Token.Comment.Preproc",foreground="sienna");
    textPad.tag_config("Token.Comment.PreprocFile",foreground="sienna");
    textPad.tag_config("Token.Literal.Number.Integer",foreground="dark orange");
    textPad.tag_config("Token.Literal.Number.Float",foreground="dark orange");
    textPad.tag_config("Token.Literal.Number.Double",foreground="dark orange");
    textPad.tag_config("Token.Comment.Single",foreground="forest green");
    textPad.tag_config("Token.Name.Builtin",foreground="RoyalBlue4");
    textPad.tag_config("Token.Literal.String",foreground="green4");
    textPad.tag_config("Token.Literal.String.Char",foreground="green4");

def DefaultText():
    f = open("defaultText.txt","r"); #Open file containing the default text
    t = f.read(); #Read the default text
    f.close();
    textPad.insert('1.0',t); #Insert the default text to the textPad
    HighlightAll(); #Highlight textPad contents

def New():
    global filePath;
    
    textPad.delete('1.0',END); #Clear textPad
    filePath = ""; #Reset filePath
    DefaultText(); #Add the default text

def Open():
    global filePath;

    #Open dialog asking which file to open
    #The filetypes shown in the dialog are the ones given in types
    #p holds the path to the file the user chose
    p = tkFileDialog.askopenfilename(filetypes=types);

    if(p == ""):
        #No file was chosen
        return;
    
    f = open(p,'r'); #Open file at p
    filePath = p; #Save p to filePath

    if(f is not None):
        #File exists
        #Pass file contents to editor
        content = f.read(); #Read contents
        f.close();
        textPad.delete('1.0',END); #Clear textPad
        textPad.insert('1.0',content); #Insert contents to textPad

        #Save the filePath for 'Open Recent'
        f = open("recent.txt",'w');
        f.write(filePath);
        f.close();
    else:
        #File doesn't exist
        return;

    HighlightAll(); #Highlight textPad

def OpenRecent():
    global filePath;

    if(not os.path.exists("recent.txt")):
        #There's no recent file
        return;

    f = open("recent.txt",'r'); #The file containing the path

    path = f.read(); #The path to the code file
    f.close();

    if(os.path.exists(path)):
        #Code file exists
        cF = open(path,'r'); #The code file

        content = cF.read(); #Read contents
        textPad.delete('1.0',END); #Clear textPad
        textPad.insert('1.0',content); #Insert contents to textPad
        cF.close();

        filePath = path;

    HighlightAll(); #Highlight textPad

def SaveAs():
    global filePath;
    
    #Open dialog asking where to save
    #The filetypes the user can save as are the ones given in types
    #If the user doesn't provide an extension, 'cpp' will be used
    #p holds the path the user chose
    p = tkFileDialog.asksaveasfilename(defaultextension=".cpp",filetypes=types);

    if(p == ""):
        #User didn't give a path
        return;
    
    f = open(p,'w'); #Create a new file (at given path) for writing
    filePath = p; #Save the path to filePath

    if(f is not None):
        #Write content in the editor to file
        data = textPad.get('1.0',END+'-1c'); #Get all text in textPad
        f.write(data); #Write text to the file
        f.close();

        #Save the filePath for 'Open Recent'
        f = open("recent.txt",'w');
        f.write(filePath);
        f.close();

def Save():
    if(filePath == ""):
        #The file hasn't been saved before. Use 'Save As'.
        SaveAs();
    else:
        #Save file to existing path
        f = open(filePath, "w"); #Open the file at filePath
        data = textPad.get('1.0',END+'-1c'); #Get all text in textPad
        f.write(data); #Write text to the file
        f.close();

def SelectAll(event):
    textPad.tag_add('sel','1.0','end');
    return "break"; #Prevent binding from firing

def Ctrl_S(event):
    #Save when pressing ctrl+s
    Save();

def Ctrl_V(event):
    #When pasting, content needs to be highlighted. To be safe, highlight all.
    HighlightAll();

def Run(event):
    Save(); #Save before execution

    #For the path of the executable, replace the extension with 'exe'
    executable = filePath.split('.')[0] + ".exe";
    dirPath = filePath.rsplit('\\',1)[0]; #The directory of source code
    
    #Move to source directory before compiling
    curDir = os.getcwd();
    os.chdir(curDir);

    #Call the Run batch file to compile and run program
    call(['Run.bat',filePath,executable]);

def Tab(event):
    global textPad;
    
    index = textPad.index('insert'); #The index of insertion

    #Every time 'Tab' is pressed, add 4 spaces (without tabbing)
    for i in range(4):
        textPad.insert(index,' ');

    return "break"; #Prevent binding from firing

def Undo(event):
    HighlightAll();

def Enter(event):
    check = KeyPress(event);

    if(check == "break"):
        return "break";
    
    index = textPad.index('insert'); #The index of insertion
    y = index.split('.')[0]; #The edited row
    x = int(index.split('.')[1]); #The edited collumn

    s = 0; #Counts consecutive spaces
    t = 0; #Counts tabs

    #Iterate through chars in row. Count how many 4-spaces-in-a-row exist.
    for i in range(x):
        c = textPad.get(y + '.' + str(i)); #Get the char at position
        if(c == ' '):
            #Found a space. Increase space counter
            s += 1;
        else:
            #Char is not a space. Reset counter
            s = 0;

        if(s == 4):
            #Found a tab (four spaces in a row). Increment t and reset s.
            t += 1;
            s = 0;

    c1 = textPad.get(y + '.' + str(x-1));
    c2 = textPad.get(y + '.' + str(x));
    
    if(c1 == '{' and c2 != '}'):
        t += 1;

    textPad.insert(y + '.' + str(x),'\n'); #Insert newLine

    for i in range(t):
        #Insert tabs in new line
        textPad.event_generate("<Tab>");

    return 'break'; #Already inserted line

def KeyRelease(event):
    #After enter is pressed to choose a word for the auto-completion, we should
    #prevent a newline from being entered. noEnter is used for the blocking.
    global noEnter;
    global trie;

    content = textPad.get('1.0',END); #Text in textPad
    l = len(content); #The length of the content
    
    if(l < 35000):
        #Only clean up the trie if the text isn't large
        trie = Trie(); #Reset trie
        for v in variables:
            if(v not in content):
                #Variable has been deleted, remove it from variables list
                del v;
            else:
                #Variable exists
                #Insert variable to trie
                trie.Insert(v);

        for k in kWords:
            #Insert keywords to trie
            trie.Insert(k);

    k = event.keycode; #The keycode of pressed button (integer)

    if(noEnter):
        if(k == 13):
            #Just used auto-completion by pressing 'Enter'.Don't add new line.
            return "break"; #Prevent binding from firing
        else:
            #Something other than 'Enter' was pressed. Reset noEnter to False.
            noEnter = False;

    c = event.char; #The inserted character
    if(c not in varChars):
        if(k != 8 and k != 46 and k != 16 and k != 222 and c != '/'):
            #Key pressed isn't an acceptable variable name character and it is
            #neither 'Backspace' nor 'Delete' nor 'Shift'.
            if(word not in variables and not word.replace('-','').isdigit()):
                #The end of the word was reached and it isn't in variables
                #and it is not a number.
                trie.Insert(word); #Insert word to trie
                variables.append(word); #Add word to list of variables
        else:
            Highlight();
    else:
        Highlight(); #Highlight the current row

def KeyPress(event):
    global selecting;
    global listBox;
    global textPad;

    print selecting;

    k = event.keycode; #The keycode of pressed button (integer)

    if(selecting):
        #listBox is on
        if(k == 40):
            #The 'Down' key was pressed
            #The user can now browse the suggestions
            listBox.focus_set(); #Set the focus on listBox
            return "break"; #Prevent binding from firing
        if(k == 13):
            #'Enter' was pressed
            SelectWord(None); #The user chose a word. Add it to textPad.
            return "break"; #Prevent binding from firing
    
    AutoComplete(event); #Start up the auto-completion system
    
def Highlight():
    RemoveTags(); #Remove the tags in this row
    
    index = textPad.index('insert'); #The index of insertion
    y = int(index.split('.')[0]); #The edited row
    
    data = textPad.get(str(y) + '.0', str(y+1) + '.0'); #The text in the row
    textPad.mark_set("range_start",str(y) + '.0'); #Set a mark at row start
    
    for token, content in lex(data, CppLexer()):
        #Set a mark from previous mark to the end of the iterated word
        textPad.mark_set("range_end", "range_start + %dc" % len(content));
        #Add token tag to iterated word
        textPad.tag_add(str(token), "range_start", "range_end");
        #Set the mark to the end of the current one (aka at the end of the word)
        textPad.mark_set("range_start", "range_end");

def HighlightAll():
    global variables;
    global trie;

    RemoveAllTags();
    
    data = textPad.get('1.0', END); #Get all the text in textPad
    textPad.mark_set("range_start",'1.0'); #Set a mark at the beginning of text

    for token, content in lex(data, CppLexer()):
        #Set a mark from previous mark to the end of the iterated word
        textPad.mark_set("range_end", "range_start + %dc" % len(content));
        #Add token tag to iterated word
        textPad.tag_add(str(token), "range_start", "range_end");
        #Set the mark to the end of the current one (aka at the end of the word)
        textPad.mark_set("range_start", "range_end");

        if(str(token) == "Token.Name"):
            #Found a variable. Add it to the list of variables.
            variables.append(str(content));
            trie.Insert(str(content));

    for v in variables:
        trie.Insert(v);

def RemoveTags():
    index = textPad.index('insert'); #The index of insertion
    y = int(index.split('.')[0]); #The edited row
    x = int(index.split('.')[1]); #The edited collumn
    
    data = textPad.get(str(y) + '.0', str(y+1) + '.0');
    textPad.mark_set("range_start",str(y) + '.0'); #The start of the line
    textPad.mark_set("range_end",str(y+1) + '.0'); #The end of the line

    for tag in textPad.tag_names():
        #delete all tags in the line, except the sel tag
        if(tag == "sel"):
            continue;
        
        textPad.tag_remove(tag, "range_start", "range_end");

def RemoveAllTags():
    for tag in textPad.tag_names():
        #delete all tags in the line, except the sel tag
        if(tag == "sel"):
            continue;
        
        textPad.tag_remove(tag, "1.0", END);

def AutoComplete(event):
    global word;
    global trie;
    global listBox;
    global selecting;
    global textPad;
    
    k = event.keycode; #The keycode of pressed button (integer)
    c = event.char; #The char of pressed button (character)
    if(c == '!' or c == '*' or c == '&'or c == '^' or c == '%'
       or c == '$' or c == '#' or c == '-' or c == '@' or c == '('
       or c == ')' or k==46 or k==107 or k==144 or k==111 or k==106
       or k==109 or k==187 or k==192 or k==190 or k==188 or k==222
       or k==186 or k==220 or k==219 or k==221 or k==17 or k==18
       or k==40 or k==39 or k==38 or k==37 or k==13 or k==32 or k==9):
        #key pressed isn't a char, reset word and hide listBox
        word = "";
        listBox.place(x=0,y=0,width=0,height=0);
        selecting = False; #User can't select a suggestion
        return;

    listBox.delete(0,END); #Delete all items in list
    
    word += c; #Add char to word
    suggestions = trie.FindWords(word); #Find all words with prefix of word

    if(suggestions == None):
        #If there are no suggestions, hide listBox
        selecting = False;
        listBox.place(x=0,y=0,width=0,height=0);
        return;

    a = yScrollbar.get()[0]; #How far yScrollbar has moved (0 : top)
    b = xScrollbar.get()[0]; #How far xScrollbar has moved (0 : left)

    #Place listBox near the insertion index
    if(a > 0 or b > 0):
        #A scrollbar is moved
        w = root.winfo_width(); #The width of the root window
        h = root.winfo_height(); #The height at the root window
        
        #listBox is placed at the bottom right corner
        listBox.place(x=w-130,y=h-190,width=115,height=175);
    else:
        #Scrollbars have not moved
        index = textPad.index('insert'); #The index of insertion
        r = int(index.split('.')[0]); #row
        col = int(index.split('.')[1]); #collumn
        
        #listBox is placed at the insertion index
        listBox.place(x=col*7.5,y=r*16.1,width=115,height=175);

    for s in suggestions:
        #Insert words with prefix of word to listBox
        listBox.insert(END,s);

    listBox.select_set(0); #Select the first element as default
    listBox.event_generate("<<ListboxSelect>>"); #Trigger selection
    
    selecting = True; #The user can now start selecting from the listBox

def SelectWord(event):
    global listBox;
    global word;
    global noEnter;
    global selecting;
    
    if(listBox.winfo_width() > 1):
        #The listBox isn't hidden, as its width is greater than 1
        w = listBox.get(ACTIVE); #Get the active selection on the listBox
        l = len(word); #The length of the written word
        #We need to complete the written word. We add at the end of the written
        #word the characters missing to get the active selection (w).
        #Thus, we need to add after the word the characters in w after the lth
        #character (aka the characters after the position : l).
        toAdd = w[l:]; #The characters to add
        
        index = textPad.index('insert');  #The index of insertion
        textPad.insert(index,toAdd); #Add the missing chars after insert index

        noEnter = True; #Block 'Enter' event (don't add newline)
        selecting = False; #The user can't select any more words
        
        word = ""; #Reset word
        Highlight(); #Highlight the row

        listBox.place(x=0,y=0,width=0,height=0); #Hide listBox
        textPad.focus_set(); #Set the focus back on textPad
        
        return "break"; #Prevent binding from firing

def KeyPress_List(event):
    k = event.keycode; #The keycode of pressed button (integer)
    if(k != 13 and k != 38 and k != 40):
        #A key other than 'Enter', 'Up' or 'Down' was pressed, remove listBox
        ListEscape();
    
def BackSpace(event):
    #When the backspace is pressed, remove listBox and reset auto-completion
    ListEscape();
    FindWord();

def MouseClick(event):
    #When the textpad is clicked on, remove listBox and reset auto-completion
    ListEscape();
    FindWord();

def FindWord():
    global word;
    global textPad;
    
    index = textPad.index('insert'); #The index of insertion
    r = int(index.split('.')[0]); #row
    col = int(index.split('.')[1]) - 2; #collumn

    word = ""; #Reset the word

    #Move back from the insertion collumn until you reach the end of the word.
    while(col >= 0):
        c = textPad.get(str(r) + '.' + str(col)); #Get the char at the collumn

        if(c not in varChars):
            #Char is not an acceptable variable name
            break; #Found our word, return

        word = c + word; #Add the char to the start of the word
        col -= 1; #Move to the left

def ListEscape():
    global textPad;
    global listBox;
    global selecting;

    listBox.place(x=0,y=0,width=0,height=0); #Hide listBox
    selecting = False; #The user can no longer select from suggestions
    textPad.focus_set(); #Set the focus on textPad



dP = sys.argv[0].rsplit('\\',1)[0]; #The path of the Editor's directory

os.chdir(dP); #Go to Editor's path (in case a file was opened)
root = Tk(); #Main window
root.title("C++ Simple Editor"); #The title of main window
root.iconbitmap('icon.ico'); #The icon of main window

#Create the text field
textPad = Text(root, wrap=NONE, undo=True, width=70, height=43.75);

#The Y-Scrollbar
yScrollbar = Scrollbar(root,orient=VERTICAL,command=textPad.yview);
yScrollbar.pack(side=RIGHT,fill=Y);
textPad["yscrollcommand"] = yScrollbar.set;

#The X-Scrollbar
xScrollbar = Scrollbar(root,orient=HORIZONTAL,command=textPad.xview);
xScrollbar.pack(side=BOTTOM,fill=X);
textPad["xscrollcommand"] = xScrollbar.set;

#Create the auto-complete listbox
listBox = Listbox(root);
listBox.config(activestyle="none");
listBox.place(x=0,y=0,width=0,height=0);

#Add key bindings for textPad
textPad.bind("<F5>",Run);
textPad.bind("<Control-s>",Ctrl_S);
textPad.bind("<Control-a>",SelectAll);
textPad.bind("<Control-KeyRelease-z>",Undo);
textPad.bind("<Control-KeyRelease-v>",Ctrl_V);
textPad.bind("<KeyRelease>",KeyRelease);
textPad.bind("<Key>",KeyPress);
textPad.bind("<BackSpace>",BackSpace);
textPad.bind("<Button-1>",MouseClick);
textPad.bind("<Tab>",Tab);
textPad.bind("<Return>",Enter);

#Add key bindings for listBox
listBox.bind("<Return>",SelectWord);
listBox.bind("<Key>",KeyPress_List);

#Create the menu
menu = Menu(root);
root.config(menu=menu);
fileMenu = Menu(menu);

##Menu tab##
menu.add_cascade(label="File",menu=fileMenu);

##Options in tab##
fileMenu.add_command(label="New",command=New);
fileMenu.add_command(label="Open...",command=Open);
fileMenu.add_command(label="Open Recent",command=OpenRecent);
fileMenu.add_command(label="Save",command=Save);

#Configure tags
TagConfig();

#Create trie for auto-complete, and insert keywords
trie = Trie();

f = open("keywords.txt",'r'); #Open keywords text file
kWords = f.read().splitlines(); #Retrieve keywords line by line
f.close();

for k in kWords:
    #Insert keywords to trie
    trie.Insert(k);

#Fill varChars
f = open('var_Chars.txt','r'); #Open text file containing acceptable var chars
chars = f.read().splitlines(); #Read chars line by line
f.close();

for c in chars:
    #Add acceptable chars to varChars
    varChars[c] = True;

#Check if there are arguments. If yes, a file was opened using the editor.
if(len(sys.argv) == 1):
    #Add default text
    DefaultText();
else:
    filePath = sys.argv[1];
    
    f = open(filePath,'r');
    s = f.read();
    f.close();
    
    textPad.insert('1.0',s); #Insert the file's content to textPad
    HighlightAll(); #Highlight textPad contents

root.tk.eval("catch {tcl_endOfWord}");
root.tk.eval("catch {tcl_startOfPreviousWord}");
root.tk.eval("set tcl_wordchars {[[:alnum:]']}");
root.tk.eval("set tcl_nonwordchars {[^_[:alnum:]']}");
textPad.pack(side=LEFT,fill=BOTH,expand=YES);
root.mainloop();
