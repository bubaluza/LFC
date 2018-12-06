import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import pprint

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        # ADICIONAR AQUI NO IF A ANÁLISE LÉXICA
        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result




class Editor(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.text = CustomText(self)
        self.vsb = tk.Scrollbar(orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        #self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.text.tag_configure("bigfont")
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.text)
        self.text.tag_configure("search", foreground="red",font='courier 10 bold')
        self.text.tag_configure("tipos", foreground="blue",font='courier 10 bold')
        self.text.tag_configure("string", foreground="green")
        self.text.tag_configure("comentario", foreground="grey",font='courier 10 italic')
		

        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        #self.text.bind("<<Change>>", self.word_search)

        self.text.insert("end", "one\ntwo\nthree\n")
        self.text.insert("end", "four\n",) # ADICIONA LINHA COM UMA TAG EXEMPLO
        self.text.insert("end", "three\n")

    def retornaTexto(self):
        return self.text.get('1.0', 'end-1c')

    def insereTextoInicio(self, contents):
        return self.text.insert('1.0',contents)

    def limpaTexto(self):
        self.text.delete('1.0','end-1c')

    def _on_change(self, event):
        self.linenumbers.redraw()
        self.word_search()

    def word_search(self):
        countVar = tk.StringVar()
        procura={"and", "array","asm", "begin", "break", "case", "const", "constructor", "continue","destructor","div","do","downto","else","end","false","file","for","function","goto","implementation","in","inline","interface","label","mod","nil","not", "object","of","on","operator","or","packed","procedure","program","record","repeat","set","shl","shr","string","then","to","true","type","unit","until","uses","var","while","with","xor"}
        self.text.tag_remove('search', '1.0', 'end')
        self.text.tag_remove('tipos', '1.0', 'end')
        self.text.tag_remove('string', '1.0', 'end')
        self.text.tag_remove('comentario', '1.0', 'end')

        tipos={"byte","Shortint","Smallint","Word","Integer","Cardinal","Longint", "Longword", "Int64", "QWord", "Real", "Single", "Double", "extended", "comp", "currency", "boolean", "bytebool", "WordBool", "LongBool"}

        countVar = tk.StringVar()
        for item in procura:
            pro="\m"+item+"\M"
            pos = self.text.search(pro, '1.0', stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)
            while pos:
                self.text.tag_add("search", pos, "%s + %sc" % (pos, countVar.get()))
                num = "%s + %sc" % (pos, countVar.get())
                print(num)
                pos = self.text.search(item,"%s + %sc" % (pos, countVar.get()) , stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)

        countVar = tk.StringVar()
        for item in tipos:
            pro="\m"+item+"\M"
            pos = self.text.search(pro, '1.0', stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)
            while pos:
                self.text.tag_add("tipos", pos, "%s + %sc" % (pos, countVar.get()))
                num = "%s + %sc" % (pos, countVar.get())
                print(num)
                pos = self.text.search(item,"%s + %sc" % (pos, countVar.get()) , stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)	

        #strings
        countVar = tk.StringVar()
        pro="\".*\"|'.*'"
        #print("pro: "+pro)
        pos = self.text.search(pro, '1.0', stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)
        while pos:
            self.text.tag_add("string", pos, "%s + %sc" % (pos, countVar.get()))
            num = "%s + %sc" % (pos, countVar.get())
            #print(num)
            #countVar.get().set(countVar.get()+1)
            #print(countVar)
            pos = self.text.search(pro,"%s + %sc" % (pos, countVar.get()) , stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)

        #comentarios
        countVar = tk.StringVar()
        pro="//.*"
        #print("pro: "+pro)
        pos = self.text.search(pro, '1.0', stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)
        while pos:
            self.text.tag_add("comentario", pos, "%s + %sc" % (pos, countVar.get()))
            num = "%s + %sc" % (pos, countVar.get())
            print(num)
            pos = self.text.search(pro,"%s + %sc" % (pos, countVar.get()) , stopindex='end-1c', count=countVar, exact=True, nocase=True,regexp=True)



    def adicionaMenu(self, root):
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=new_command)
        filemenu.add_command(label="Open", command=open_command)
        filemenu.add_command(label="Save", command=donothing)
        filemenu.add_command(label="Save as...", command=save_command)
        filemenu.add_command(label="Close", command=donothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=exit_command)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=donothing)

        editmenu.add_separator()

        editmenu.add_command(label="Cut", command=donothing)
        editmenu.add_command(label="Copy", command=donothing)
        editmenu.add_command(label="Paste", command=donothing)
        editmenu.add_command(label="Delete", command=donothing)
        editmenu.add_command(label="Select All", command=donothing)

        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=about_command)
        menubar.add_cascade(label="Help", menu=helpmenu)
        root.config(menu=menubar)

def donothing():
   filewin = tk.Toplevel(root)
   button = tk.Button(filewin, text="Essa função no menu não foi implementada ainda ou é só para enfeite")
   button.pack()


def open_command():
        file = filedialog.askopenfile(parent=root,mode='rb',title='Select a file')
        if file != None:
            contents = file.read()
            editor.limpaTexto()
            editor.insereTextoInicio(contents)
            file.close()
            root.title("Editor de Turbo Pascal - " + file.name)

def save_command():
    file = filedialog.asksaveasfile(mode='w')
    #print(file.name)
    root.title("Editor de Turbo Pascal - " + file.name)
    if file != None:
    # slice off the last character from get, as an extra return is added
        data = editor.retornaTexto()
        file.write(data)
        file.close()

def exit_command():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def about_command():
    label = messagebox.showinfo("About", "Editor de texto para a linguagem Turbo Pascal\nAlunos: Gabriel Schiller, João Krüger, Michel Hoekstra, Paulo Machado, Pedro Neto, Ricardo Harms")

def new_command():
    if messagebox.askyesno("New File", "Do you want to save the current file? Data will be lost otherwise."):
        save_command()
    editor.limpaTexto()
    root.title("Editor de Turbo Pascal - Novo arquivo")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Editor de Turbo Pascal")
    editor = Editor(root)
    editor.pack(side="top", fill="both", expand=True)
    editor.adicionaMenu(root)
    #print (vars(root))
    #print (vars(editor.master))
    #print (vars(editor))

    #countVar = tk.StringVar()
    #pos = editor.text.search('quatro', '1.0', stopindex='end-1c', count=countVar)
    #print(pos)
    #print(countVar.get())
    #editor.text.tag_configure("search", background="green")
    #if(pos==""):
    #    print("bilada")
    #print (editor.retornaTexto())

    root.mainloop()


#https://www.tutorialspoint.com/python/tk_text.htm
