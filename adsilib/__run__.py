from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .build_my_library import *

if sys.version_info[0] > 2:
    from tkinter import *
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    import tkinter.simpledialog as tkSimpleDialog
else:
    from Tkinter import *
    import tkFileDialog
    import tkMessageBox
    import tkSimpleDialog


def setup_window(window, objects, title_font=None, main_font=None, button_font=None, entries_bd=3):

    if button_font is None:
        button_font = ['times', 15, 'bold']

    if main_font is None:
        main_font = ['times', 15]

    if title_font is None:
        title_font = ['times', 17, 'bold']

    for row in range(len(objects)):
        if len(objects[row]) == 0:
            label_empty = Label(window, text='')
            label_empty.grid(row=row, column=100)
        else:
            for obj in objects[row]:
            
                if isinstance(obj[0], str):
                    if obj[0] == ' ':
                        obj[0] = Label(window, text='')

                if obj[0].winfo_class() == 'Button':
                    obj[0].configure(font=button_font)
                elif obj[0].winfo_class() == 'Entry':
                    obj[0].configure(bd=entries_bd, font=main_font)
                elif obj[0].winfo_class() in ['Label', 'Radiobutton']:
                    if len(obj) == 5:
                        if obj[4] == 'title':
                            obj[0].configure(font=title_font)
                        else:
                            obj[0].configure(font=main_font)
                    else:
                        obj[0].configure(font=main_font)

                if len(obj) >= 4:
                    obj[0].grid(row=row, column=obj[1], columnspan=obj[2], rowspan=obj[3])
                elif len(obj) == 3:
                    obj[0].grid(row=row, column=obj[1], columnspan=obj[2])
                else:
                    obj[0].grid(row=row, column=obj[1])


def initialise_window(window, window_name, windows_to_hide, windows_to_close, exit_python, other_exit_command=None):

    def exit_command():

        for i in windows_to_close:
            i.destroy()

        for i in windows_to_hide:
            i.withdraw()

        if other_exit_command:
            other_exit_command()

        if exit_python:
            os._exit(-1)

    window.wm_title(window_name)
    window.protocol('WM_DELETE_WINDOW', exit_command)

    window.withdraw()


def finalise_window(window, position=5):

    window.update_idletasks()

    if position == 1:
        x = 0
        y = 0

    elif position == 2:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = 0

    elif position == 3:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = 0

    elif position == 4:
        x = 0
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 5:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 6:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2

    elif position == 7:
        x = 0
        y = window.winfo_screenheight() - window.winfo_reqheight()

    elif position == 8:
        x = (window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
        y = window.winfo_screenheight() - window.winfo_reqheight()

    elif position == 9:
        x = window.winfo_screenwidth() - window.winfo_reqwidth()
        y = window.winfo_screenheight() - window.winfo_reqheight()

    else:
        x = 0
        y = 0

    window.geometry('+%d+%d' % (x, y))

    window.update_idletasks()

    window.lift()
    window.wm_attributes("-topmost", 1)
    window.after_idle(window.attributes, '-topmost', 0)

    window.deiconify()


def run_app():

    my_library = DataBase()

    global papers, papers_dic
    papers = []
    papers_dic = {}

    def search_ads(*entry):

        if not entry:
            pass

        global papers, papers_dic

        papers = ads.SearchQuery(q=entry1.get(),
                                 fl=['bibcode', 'title', 'author', 'year', 'citation_count', 'abstract'])
        papers = [[ff.citation_count, ff.bibcode, ff.title, ff.author, ff.year, ff.abstract] for ff in papers]
        papers.sort()
        papers_dic = {}
        listbox.delete(0, END)
        for paper in papers[::-1]:
            papers_dic[paper[1]] = {'title': paper[2][0], 'author': paper[3], 'year': paper[4], 'abstarct': paper[5]}
            authors = ''
            for i in paper[3][:-1]:
                authors += i
                authors += '; '
            for i in paper[3][-1]:
                authors += i
            listbox.insert(END, '  {0}{1} {2}     '.format(
                paper[0], ' ' * abs(3 - len(str(paper[0]))),
                paper[1]) +
                paper[2][0])
            test = my_library.search_library(paper[1])
            if test:
                test = test[0]['call']
            else:
                test = '-'
            listbox.insert(END, '  {0}{1}  '.format(test, ' ' * abs(35 - len(test))) + authors)
        if len(papers) == 0:
            listbox.insert(END, 'No results found.')

    def get_bibcode():

        item = listbox.get(listbox.curselection()).split()[1]
        if item not in papers_dic:
            item = listbox.get((listbox.curselection()[0] - 1, )).split()[1]

        return item

    def add_to_library():
        bibcode = get_bibcode()
        my_library.add_to_library(bibcode)
        test = my_library.search_library(bibcode)
        if test:
            if len(test[1]) > 0:

                similar = ''
                for i in test[1]:
                    similar += i['call'] + '\n' + i['title'][0] + '\n'

                tkMessageBox.showinfo('Reference in library',
                                      'Call reference as: \n' + test[0]['call'] + '\n\nSimilar references: \n\n' +
                                      similar)
            else:
                tkMessageBox.showinfo('Reference in library', 'Call reference as: \n' + test[0]['call'])

            root.clipboard_clear()
            root.clipboard_append(test[0]['call'])

        else:
            tkMessageBox.showinfo('Reference not added', 'Something went wrong...')

        search_ads()

    def show_abstarct():
        bibcode = get_bibcode()
        root2 = Tk()
        root2.wm_title(papers_dic[bibcode]['title'])
        x = root2.winfo_screenwidth() / 2
        y = root2.winfo_screenheight() / 2
        root2.geometry('%dx%d' % (x, y))
        x = root2.winfo_screenwidth() / 4
        y = 0
        root2.geometry('+%d+%d' % (x, y))
        root2.update_idletasks()
        tt = Text(root2)
        tt.pack()
        tt.insert(END, '\n')
        for i in papers_dic[bibcode]['author'][:1]:
            tt.insert(END, i.split(',')[0])
        tt.insert(END, bibcode[:4])
        tt.insert(END, '\n')
        tt.insert(END, papers_dic[bibcode]['title'])
        tt.insert(END, '\n\n')
        for i in papers_dic[bibcode]['author'][:-1]:
            tt.insert(END, i)
            tt.insert(END, '; ')
        for i in papers_dic[bibcode]['author'][-1:]:
            tt.insert(END, i)
        tt.insert(END, '\n\n')
        tt.insert(END, papers_dic[bibcode]['abstarct'])
        root2.mainloop()

    def update_bib_file(*entry):

        if not entry:
            pass

        my_library.export_bib(entry41.get())
        tkMessageBox.showinfo('Updating .bib file.', '.bib file updated successfully')

    def compile_tex(*entry):

        if not entry:
            pass

        tex_file = entry42.get()
        original_dir = os.path.abspath('.')
        os.chdir(os.path.split(tex_file)[0])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.system('bibtex ' + os.path.split(tex_file)[1].split('.')[0])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.chdir(original_dir)
        tkMessageBox.showinfo('Compiling .tex file.', '.tex file compiled successfully')

    def update_bib_compile_tex(*entry):

        if not entry:
            pass

        my_library.export_bib(entry41.get())
        tex_file = entry42.get()
        original_dir = os.path.abspath('.')
        os.chdir(os.path.split(tex_file)[0])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.system('bibtex ' + os.path.split(tex_file)[1].split('.')[0])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.system('pdflatex ' + os.path.split(tex_file)[1])
        os.chdir(original_dir)
        tkMessageBox.showinfo('Compiling tex file.', '.bib file updated successfully and '
                                                     '\n .tex file compiled successfully')

    def choose_bib_file():
        bib_file = tkFileDialog.askopenfilename()
        entry41.delete(0, END)
        entry41.insert(0, bib_file)

    def choose_tex_file():
        tex_file = tkFileDialog.askopenfilename()
        entry42.delete(0, END)
        entry42.insert(0, tex_file)

    def update_library():
        my_library.update_library()
        tkMessageBox.showinfo('Updating library for arXiv papers.', 'Update completed')

    root = Tk()
    xx = root.winfo_screenwidth() / 2
    yy = root.winfo_screenheight() / 2
    root.geometry('%dx%d' % (xx, yy))
    initialise_window(root, 'ADS search', [], [root], True)

    frame1 = Frame(root)
    entry1 = Entry(frame1, width=30)
    button1 = Button(frame1, text="Search", command=search_ads)
    entry1.bind('<Return>', search_ads)
    setup_window(frame1, [[], [[' ', 0], [entry1, 1], [button1, 2]], []])
    frame1.pack()

    frame2 = Frame(root)
    scrollbar = Scrollbar(frame2)
    listbox = Listbox(frame2, yscrollcommand=scrollbar.set)
    listbox.config(font=['courier', 15])
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox.pack(expand=True, fill=BOTH)
    frame2.pack(expand=True, fill=BOTH)

    frame3 = Frame(root)
    button31 = Button(frame3, text="Add to library", command=add_to_library)
    button32 = Button(frame3, text="Show abstract", command=show_abstarct)
    setup_window(frame3, [[], [[' ', 0], [button31, 1], [button32, 2]], []])
    frame3.pack()

    frame4 = Frame(root)
    button40 = Button(frame4, text="Update library for arXiv papers", command=update_library)
    button41 = Button(frame4, text="Choose .bib file", command=choose_bib_file)
    entry41 = Entry(frame4, width=30)
    button42 = Button(frame4, text="Update .bib file", command=update_bib_file)
    button43 = Button(frame4, text="Choose .tex file", command=choose_tex_file)
    entry42 = Entry(frame4, width=30)
    button44 = Button(frame4, text="Compile .tex file", command=compile_tex)
    button45 = Button(frame4, text="Update .bib file and compile .tex file", command=update_bib_compile_tex)
    setup_window(frame4,
                 [[[button40, 1]],
                  [[button41, 0], [entry41, 1], [button42, 2]],
                  [[button43, 0], [entry42, 1], [button44, 2]],
                  [[button45, 1]],
                  []])
    frame4.pack()

    finalise_window(root, position=5)
    root.mainloop()
