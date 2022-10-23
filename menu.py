from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import datetime
import time

from pymongo import MongoClient
import pymongo

client = MongoClient()
db = client.finances
paragony = db.paragony

root = Tk()
root.geometry("1200x800")

l = []
suma = 0
sumP = 0
lKat = ['','']  # lista wszystkich kategorii
P = []
D = {}
b = True
selectedDate = 0

def dataSort(a):
    return a['data']

def refresh():
    global P
    global lKat
    global D
    global sumP

    P = []
    lKat = []
    tempKat = {}

    for p in paragony.find():
        P.insert(0, p)
        for r in p['rzeczy']:
            tempKat[r['kategoria']] = 0

    P.sort(reverse=True, key=dataSort)

    for k in tempKat:
        lKat.append(k)
    lKat.append('+')

    D = {}
    for p in P:
        if p['data'] in D:
            D[p['data']].append(p) # = int(D[p['data']]) + int(p['suma'])
        else:
            D[p['data']] = []
            D[p['data']].append(p)

    for item in dbTree.get_children():
        dbTree.delete(item)
    id = 0
    for i in D:
        suma = 0
        for k in range(len(D[i])):
            suma = suma + int(D[i][k]['suma'])
        dbTree.insert(parent='', index='end', iid=id, text='Parent',
                      values=(i, '', "{:.2f}".format(float(suma)/100)))
        id = id+1
    b = True
    nPar_l.config(text="Ilość paragonów: " + str(len(P)))
    
    selectetKatVar.set(' ')
    menu = kategoria_s["menu"]
    menu.delete(0, "end")
    for choice in lKat:
        menu.add_command(label=choice, command=tk._setit(selectetKatVar, choice, nowaKategoria))
    dtl.config(text='')
    skll.config(text='')
    suma_l.config(text="Suma 0")
    

def addOne():
    errorMessage = ''
    try:
        int(cena_e.get())
    except ValueError:
        errorMessage = errorMessage + '\n' + "Wpisz cenę w groszach"
    else:
        pass
    if selectetKatVar.get() == ' ':
        errorMessage = errorMessage + '\n' + "Wybierz kategorię"
    if nazwa_e.get() == '':
        errorMessage = errorMessage + '\n' + "Wpisz nazwę"
    if selectetKatVar.get() == '+' and kategoria_e.get() == '':
        errorMessage = errorMessage + '\n' + "Wpisz kategorię"
    try:
        int(ile_e.get())
    except ValueError:
        errorMessage = errorMessage + '\n' + 'Pole "ile" ma być liczbą'
    else:
        if int(ile_e.get()) < 0:
            errorMessage = errorMessage + '\n' + 'Pole "ile" ma być liczbą większą od zera'

    if len(errorMessage) > 0:
        messagebox.showinfo('Error:', errorMessage)
    else:
        global suma
        suma = 0
        if selectetKatVar.get() == '+':
            kat = kategoria_e.get()
            kategoria_e.grid_forget()
        else:
            kat = selectetKatVar.get()
        rzecz = {
            "nazwa": nazwa_e.get(),
            "kategoria": kat,
            "cena": cena_e.get()
        }

        for i in range(int(ile_e.get())):
            l.append(rzecz)

        '''
        # destroy all widgets from frame
        for widget in treeframe.winfo_children():
            widget.destroy()
        '''
        # clear treeview
        for item in tree.get_children():
            tree.delete(item)

        dtl.config(text=data_e.get())
        skll.config(text=sklep_e.get())

        id = 0
        for i in l:
            suma = suma + int(i['cena'])
            tree.insert(parent='', index='end', iid=id, text='Parent',
                        values=(i['nazwa'], i['kategoria'], "{:.2f}".format(float(i['cena'])/100)))
            id = id + 1

        suma_l.config(text="Suma "+str("{:.2f}".format(float(suma)/100)))

        nazwa_e.delete(0, END)
        kategoria_e.delete(0, END)
        cena_e.delete(0, END)
        ile_e.delete(0, END)
        ile_e.insert(0, 1)
        nazwa_e.focus()

        selectetKatVar.set(' ')


def submit():
    global l
    global P
    errorMessage = ''
    try:
        datetime.datetime.strptime(data_e.get(), '%Y/%m/%d')
    except ValueError:
        errorMessage = errorMessage + '\n' + 'Wpisz poprawną datę "yyyy/mm/dd"'
    if sklep_e.get() == '':
        errorMessage = errorMessage + '\n' + "Wpisz sklep"
    if len(errorMessage) > 0:
        messagebox.showinfo('Error:', errorMessage)
    else:
        X = {
            "data": data_e.get(),
            "sklep": sklep_e.get(),
            "rzeczy": l,
            "suma": suma
        }
        paragony.insert_one(X)

        for item in tree.get_children():
            tree.delete(item)

        l = []

        data_e.delete(0, END)
        t = time.strftime("%Y/%m/%d", time.localtime())
        data_e.insert(0, t)
        sklep_e.delete(0, END)
        nazwa_e.delete(0, END)
        kategoria_e.delete(0, END)
        cena_e.delete(0, END)
        ile_e.delete(0, END)
        ile_e.insert(0, 1)

        data_e.focus()

        refresh()

def onClick(selected):
    return

def onDoubleClick(selected):
    global P
    global b
    global selectedDate
    # clear treeview
    if b == True:
        dbInfoTree.pack(padx=10)
        if dbTree.focus() == '':
            return
        selected = int(dbTree.focus())
        selectedDate = dbTree.item(selected)['values'][0]
        for item in dbTree.get_children():
            dbTree.delete(item)
        id = 0
        for i in D[selectedDate]:
            dbTree.insert(parent='', index='end', iid=id, text='Parent', values=(
                i['data'], i['sklep'], "{:.2f}".format(float(i['suma'])/100)))
            id = id+1
        b = False
        backButton.grid(row=0, column=0)
        deleteButton.grid(row=0, column=1)
    else:
        for item in dbInfoTree.get_children():
            dbInfoTree.delete(item)
        if dbTree.focus() == '':
            return
        selected = int(dbTree.focus())
        id = 0
        for i in D[selectedDate][selected]['rzeczy']:
            dbInfoTree.insert(parent='', index='end', iid=id, text='Parent', values=(
                i['nazwa'], i['kategoria'], "{:.2f}".format(float(i['cena'])/100)))
            id = id+1

def back():
    global b
    for item in dbTree.get_children():
        dbTree.delete(item)
    id = 0
    for i in D:
        suma = 0
        for k in range(len(D[i])):
            suma = suma + int(D[i][k]['suma'])
        dbTree.insert(parent='', index='end', iid=id, text='Parent',
                      values=(i, '', "{:.2f}".format(float(suma)/100)))
        id = id+1
    backButton.grid_forget()
    deleteButton.grid_forget()
    dbInfoTree.pack_forget()
    b = True

def deleteP():
    global b
    selectedP = D[selectedDate][int(dbTree.focus())]
    m = 'Usunąć paragon z ' + str(selectedP['data']) + ' na sumę ' + str(selectedP['suma'])
    if messagebox.askyesno('Delete', m):
        for item in dbInfoTree.get_children():
            dbInfoTree.delete(item)
        if dbTree.focus() == '':
            return
        print(selectedP['_id'])
        paragony.delete_one({'_id': selectedP['_id']})
        b = True
        dbInfoTree.pack_forget()
        refresh()


def listaKategorii():

    result = []
    return result

def nowaKategoria(selected):
    selected = selectetKatVar.get()
    if selected == "+":
        print(selected)
        kategoria_e.grid(row=0, column=1, sticky=W)
    else:
        kategoria_e.grid_forget()


'''
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=48)
'''
# font change
root.option_add("*Font", (None, 18))


input_frame = LabelFrame(root, text="input")
input_frame.grid(row=0, column=0)


data_l = Label(input_frame, text="Data")
data_l.grid(row=0, column=0, sticky=E)
sklep_l = Label(input_frame, text="Sklep")
sklep_l.grid(row=1, column=0, sticky=E)
nazwa_l = Label(input_frame, text="Nazwa")
nazwa_l.grid(row=2, column=0, sticky=E)

katFrame = Frame(input_frame)
katFrame.grid(row=3, column=1, sticky=W)
kategoria_l = Label(input_frame, text="Kategoria")
kategoria_l.grid(row=3, column=0, sticky=E)
#kategoria_ls = Label(input_frame, text="Kategoria")
#kategoria_ls.grid(row=4, column=0, sticky=E)
cena_l = Label(input_frame, text="Cena (gr)")
cena_l.grid(row=5, column=0, sticky=E)
ile_l = Label(input_frame, text="Ile")
ile_l.grid(row=6, column=0, sticky=E)

selectetKatVar = StringVar(root)
selectetKatVar.set(lKat[0])  # default value

data_e = Entry(input_frame, width=10)
data_e.grid(row=0, column=1, padx=5, sticky=W)
t = time.strftime("%Y/%m/%d", time.localtime())
data_e.insert(0, t)
sklep_e = Entry(input_frame, width=15)
sklep_e.grid(row=1, column=1, padx=5, sticky=W)
nazwa_e = Entry(input_frame, width=21)
nazwa_e.grid(row=2, column=1, padx=5, sticky=W)
kategoria_s = OptionMenu(katFrame, selectetKatVar,
                         *lKat, command=nowaKategoria)
kategoria_s.grid(row=0, column=0, padx=6, pady=2, sticky=W)
kategoria_e = Entry(katFrame, width=15)
cena_e = Entry(input_frame, width=8)
cena_e.grid(row=5, column=1, padx=5, sticky=W)
ile_e = Entry(input_frame, width=2)
ile_e.grid(row=6, column=1, padx=5, sticky=W)
ile_e.insert(0, 1)

data_e.focus()

addButton = Button(input_frame, text="Dodaj artykuł >>", command=addOne)
addButton.grid(row=6, column=1, padx=10, pady=10, sticky=E)




# info frame
treeframe = Frame(root)
treeframe.grid(row=0, column=1)


dtl = Label(treeframe, text=data_e.get())
dtl.pack()
skll = Label(treeframe, text=sklep_e.get())
skll.pack()


tree = ttk.Treeview(treeframe)

tree['columns'] = ("Nazwa", "Kategoria", "Cena")

# add width=0 and stretch=NO to get rid of
tree.column('#0', width=0, stretch=NO)
tree.column('Nazwa', anchor=W, width=200)
tree.column('Kategoria', anchor=W, width=150)
tree.column('Cena', anchor=E, width=80)
tree.heading('Nazwa', text='Nazwa', anchor=W)
tree.heading('Kategoria', text='Kategoria', anchor=W)
tree.heading('Cena', text='Cena', anchor=E)
tree.pack()

suma_l = Label(treeframe, text="Suma "+str(suma))
suma_l.pack()

submitButton = Button(treeframe, text="DODAJ PARAGON",
                      command=submit, font='Georgia 25')
submitButton.pack()

# db frame

dbFrame = Frame(root)
dbFrame.grid(row=1, column=0)

dbTree = ttk.Treeview(dbFrame)

dbTree['columns'] = ('Data', 'Sklep', 'Suma')

# add width=0 and stretch=NO to get rid of
dbTree.column('#0', width=0, stretch=NO)
dbTree.column('Data', anchor=W, width=120)
dbTree.column('Sklep', anchor=W, width=180)
dbTree.column('Suma', anchor=E, width=80)
dbTree.heading('Data', text='Data', anchor=W)
dbTree.heading('Sklep', text='Sklep', anchor=W)
dbTree.heading('Suma', text='Suma', anchor=E)
dbTree.pack(padx=20, pady=20)

nPar_l = Label(dbFrame, text="Ilość paragonów: " + str(id))  # ilość paragonów
nPar_l.pack()
refresh()
buttonsFrame = Frame(dbFrame)
buttonsFrame.pack()
backButton = Button(buttonsFrame, text="<<<", command=back)
deleteButton = Button(buttonsFrame, text="Delete", command=deleteP)


dbTree.bind("<Double-1>", onDoubleClick)  # <Button-1>, <Double-1> or <Shift-Button-1>
dbTree.bind("<Button-1>", onClick)  # <Button-1> or <Double-1>

dbInfoFrame = Frame(root)
dbInfoFrame.grid(row=1, column=1)

dbInfoTree = ttk.Treeview(dbInfoFrame)

dbInfoTree['columns'] = ('Nazwa', 'Kategoria', 'Cena')

# add width=0 and stretch=NO to get rid of
dbInfoTree.column('#0', width=0, stretch=NO)
dbInfoTree.column('Nazwa', anchor=W, width=250)
dbInfoTree.column('Kategoria', anchor=W, width=130)
dbInfoTree.column('Cena', anchor=W, width=80)
dbInfoTree.heading('Nazwa', text='Nazwa', anchor=W)
dbInfoTree.heading('Kategoria', text='Kategoria', anchor=W)
dbInfoTree.heading('Cena', text='Cena', anchor=W)


style = ttk.Style()
style.configure("Treeview", rowheight=30, font=(None, 18))
'''
Font_tuple = ("Comic Sans MS", 20, "bold")
  
# Parsed the specifications to the
# Text widget using .configure( ) method.
sample_text.configure(font = Font_tuple)
'''
mainloop()
