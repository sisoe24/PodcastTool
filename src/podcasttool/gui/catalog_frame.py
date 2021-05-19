"""Catalog page frame from the gui.

From here you can modify the name catalog by adding and deleting other names.
The module will create the audio files for the newly created names.
"""
import os
import json
import logging
import pathlib

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from podcasttool import util

LOGGER = logging.getLogger('podcasttool.catalog')


class CatalogFrame(tk.Frame):
    """Catalog page of the gui."""
    _catalog_list = util.catalog_names()
    _updated_names = {"docenti": [], "corsi": []}
    _delete_audio = []

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        _catalog_frame = ttk.Frame(self, width=400, height=800)
        _catalog_frame.grid(column=0, row=0, rowspan=2)
        self.vertical_scrollbar = ttk.Scrollbar(_catalog_frame)

        self._tree_list = ttk.Treeview(_catalog_frame, height=24,
                                       selectmode='browse',
                                       yscrollcommand=self.vertical_scrollbar.set,
                                       columns=("names_short", "names_long"))
        self._tree_list.grid(column=0, row=0, columnspan=3, rowspan=3)
        self._generate_tree_columns()

        self.vertical_scrollbar.config(command=self._tree_list.yview)

        self.vertical_scrollbar.grid(
            column=3, row=0, rowspan=3,  sticky=tk.N + tk.S)

        self._options_frame = ttk.Frame(self, width=300, height=500)
        self._options_frame.grid(column=2, row=0, sticky=tk.N)
        self._options_frame.grid_propagate(False)

        # load list frame
        _label_lista = ttk.LabelFrame(self._options_frame, text="Liste nomi")
        _label_lista.grid(column=3, row=0, sticky=tk.NW)

        self._selected_catalog = ttk.Combobox(_label_lista,
                                              value=["docenti", "corsi"],
                                              width=10, state="readonly")
        self._selected_catalog.grid(column=0, row=0, pady=10, sticky=tk.E)

        ttk.Button(_label_lista, text="Carica lista",
                   command=self._load_catalog).grid(column=1, row=0, padx=10)

        # insert new frame
        self._insert_frame = ttk.LabelFrame(self._options_frame,
                                            text="Aggiungi nuovo nome")
        self._insert_frame.grid(column=3, row=1,  ipady=5, sticky=tk.N)

        ttk.Label(self._insert_frame, text="abbr.").grid(column=0, row=1,
                                                         sticky=tk.W)
        self._short_name = ttk.Entry(self._insert_frame)
        self._short_name.grid(column=1, row=1)

        ttk.Label(self._insert_frame, text="intero").grid(column=0, row=2,
                                                          sticky=tk.W)
        self._long_name = ttk.Entry(self._insert_frame)
        self._long_name.grid(column=1, row=2)

        self._course = None

        ttk.Label(self._insert_frame, text="lang").grid(column=0, row=4,
                                                        sticky=tk.W)
        self._lang_select = ttk.Combobox(self._insert_frame, state="readonly",
                                         value=["it", "en"], width=5)
        self._lang_select.grid(column=1, row=4, sticky=tk.W)
        self._lang_select.current(0)

        ttk.Button(self._insert_frame, text="Aggiungi",
                   command=self._insert_to_catalog).grid(column=1, row=4,
                                                         sticky=tk.E)

        self._btn_save = ttk.Button(self._options_frame,
                                    text="Salva modifiche", state="disabled",
                                    command=self._save_new_catalog)
        self._btn_save.grid(column=3, row=2, pady=15, sticky=tk.E)

        ttk.Button(self._options_frame, text="Cancella nome selezionato",
                   command=self._delete_selected).grid(
                       column=3, row=3, sticky=tk.E)

    def get_selected(self):
        item = self._tree_list.item(self._tree_list.selection())
        print(item)

    def _course_path(self):
        """Add course path to new courses."""
        value = ["ALP", "ELM", "EMP", "TTS"]
        if self._selected_catalog.get() == "corsi":

            ttk.Label(self._insert_frame, text="corso",
                      name="corse_l").grid(column=0, row=3)

            self._course = ttk.Combobox(self._insert_frame, value=value,
                                        state="readonly", width=5,
                                        name="corse_p")
            self._course.grid(column=1, row=3, sticky=tk.E)
            # self._course = course.get()

        if self._selected_catalog.get() == "docenti":
            for widget in self._insert_frame.winfo_children():
                if "corse" in widget.winfo_name():
                    widget.destroy()

    @ property
    def _language(self):
        """Return the language selected: it or eng."""
        return self._lang_select.get()

    def _check_name_size(self, course_name):
        """Check if name course is 3 letters long otherwise raise error."""
        if self.get_catalog == "corsi" and not len(course_name) == 3:
            raise ValueError("Course name has to be 3 letters long")

    def _generate_tree_columns(self):
        """Generate columns for the treeview widget."""
        self._tree_list["show"] = "headings"
        self._tree_list.heading('names_short', text='Nome abbreviato')
        self._tree_list.column('names_short', width=130)
        self._tree_list.heading('names_long', text='Nome intero')
        self._tree_list.column('names_long', width=300)

        self._tree_list.tag_configure("oddrow", background='gray90')
        self._tree_list.tag_configure("evenrow", background='gray99')

    @property
    def get_catalog(self):
        """Return the catalog name selected from the combobox widget."""
        return self._selected_catalog.get()

    def _refresh_list(self):
        """Refresh (delete) list in treeview widget when loading other list."""
        self._tree_list.delete(*self._tree_list.get_children())

    def _reset_list(self):
        """When loading catalog, reset modification that have not be saved."""
        self._updated_names = {"docenti": [], "corsi": []}
        self._catalog_list = util.catalog_names()

    def _load_catalog(self):
        """Load name list into treeview widget."""
        self._reset_list()
        self._refresh_list()
        self._course_path()

        # self._btn_insert["state"] = "active"

        row_colors = ["oddrow", "evenrow"]
        try:
            catalog_names = sorted(
                self._catalog_list[self.get_catalog].items())
        except KeyError:
            return
        for index, names in enumerate(catalog_names):
            if index % 2 == 0:
                self._tree_list.insert('', index, names[0],
                                       tags=(row_colors[index - index]))
            else:
                self._tree_list.insert('', index, names[0],
                                       tags=(row_colors[index - index + 1]))

            self._tree_list.set(names[0], 'names_short', names[0])
            try:
                self._tree_list.set(names[0], 'names_long',
                                    names[1]["course_name"])
            except TypeError:
                self._tree_list.set(names[0], 'names_long', names[1])

    def _delete_selected(self):
        """Delete selected element from treeview widget."""

        try:
            selected_item = self._tree_list.selection()[0]
        except IndexError:
            messagebox.showinfo(title="PodcastTool",
                                message="Nessun nome selezionato")
            return
        confirm = messagebox.askyesno(title="PodcastTool",
                                      message=(f"Cancellare: {selected_item}?")
                                      )
        if confirm:
            item = self._tree_list.item(self._tree_list.selection())
            audio_name = item['values'][1].replace(' ', '_')
            self._delete_audio.append(f'{audio_name}.mp3')

            self._tree_list.delete(selected_item)
            self._delete_from_catalog(selected_item)
            self._btn_save["state"] = "active"

    def _delete_from_catalog(self, delete_key):
        """Delete key from class catalog list."""
        self._catalog_list[self.get_catalog].pop(delete_key)

    def _get_new_names(self):
        """Return a tuple with new names to insert taken from Entry widget.

        Return:
            tuple - short_name and long_name variables.
        """
        if not self._short_name.get() or not self._long_name.get():
            messagebox.showinfo(title="Errore", message="Nome invalido")
            return None

        _ = self._short_name.get().strip()

        # TODO: should do better checking of typos example:
        # if there are two spaces then it will insert 2 trailing
        if self.get_catalog == "docenti":
            short_name = _.replace(" ", "_").title()
        else:
            short_name = _.replace(" ", "_").upper()
        del _

        long_name = self._long_name.get().strip().title()
        return (short_name, long_name)

    def _insert_to_catalog(self):
        """Insert new name into treeview widget."""
        try:
            short_name, long_name = self._get_new_names()
            self._check_name_size(short_name)

        except TypeError:
            messagebox.showinfo(title="Errore",
                                message="Nessun nome inserito")

        except tk._tkinter.TclError:
            messagebox.showerror(title="Errore", message="Nome esiste già!")

        except ValueError:
            messagebox.showerror(
                title="nome corso",
                message="Nome del corso dovrebbe avere solo 3 lettere")
        else:
            if self.get_catalog == "docenti":
                self._catalog_list[self.get_catalog].update(
                    {short_name: long_name})

            else:
                course_path = self._course.get()
                if not course_path:
                    messagebox.showerror(message="manca codice corso")
                    return
                self._catalog_list[self.get_catalog].update(
                    {short_name: {"course_name": long_name,
                                  "course_path": course_path}})

            self._tree_list.insert("", 0, short_name)
            self._tree_list.set(short_name, 'names_short', short_name)
            self._tree_list.set(short_name, 'names_long', long_name)

            self._updated_names[self.get_catalog].append(
                [long_name, self._language])
            self._btn_save["state"] = "active"

    def _save_new_catalog(self):
        """Save new verison of catalog after delete or added new names."""
        # modification = [_ for _ in self._updated_names.values() if _]
        with open(util.catalog_file(), "w") as json_file:
            json.dump(self._catalog_list, json_file, indent=True)
        self.update()
        self._update_audio_library()
        if self._delete_audio:
            self._delete_new_audio()
        messagebox.showinfo(message="Modifiche salvate!")

    def _delete_new_audio(self):
        for file in pathlib.Path(util.USER_AUDIO).glob('*mp3'):
            if file.name in self._delete_audio:
                LOGGER.debug('Deleting file: %s', file)
                os.remove(file)

    def _update_audio_library(self):
        """Update audio library with deleting or adding the modifications."""
        for _, new_names in self._updated_names.items():
            for index, new_name in enumerate(new_names, 20):
                name, lang = new_name

                if util.generate_audio(text=name, path=util.USER_AUDIO, lang=lang):
                    msg = f"Generating audio for:\n{name}"
                else:
                    msg = f'Problems generating audio for:\n{name}\nPlease check log file'

                ttk.Label(self._options_frame, text=msg).grid(
                    column=3, row=index, sticky=tk.W, padx=5)
