"""Catalog page frame from the gui.

From here you can modify the name catalog by adding and deleting other names.
The module will create the audio files for the newly created names.
"""
import json

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from podcasttool import util


class CatalogFrame(tk.Frame):
    """Catalog page of the gui."""
    _catalog_list = util.catalog_names()
    _updated_names = {}

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        _catalog_frame = ttk.Frame(self, width=420, height=800)
        _catalog_frame.grid(column=0, row=0, rowspan=2)

        _options_frame = ttk.Frame(self, width=300, height=500)
        _options_frame.grid(column=1, row=0, sticky=tk.N)
        _options_frame.grid_propagate(False)

        self._tree_list = ttk.Treeview(_catalog_frame, height=24,
                                       columns=("names_short", "names_long"))
        self._tree_list.grid(column=0, row=0, columnspan=3, rowspan=3)
        self._generate_tree_columns()

        # load list frame
        _label_lista = ttk.LabelFrame(_options_frame, text="Liste nomi")
        _label_lista.grid(column=3, row=0, sticky=tk.NW)

        self._selected_catalog = ttk.Combobox(_label_lista,
                                              value=["docenti", "corsi"],
                                              width=10, state="readonly")
        self._selected_catalog.grid(column=0, row=0, pady=10, sticky=tk.E)

        ttk.Button(_label_lista, text="Carica lista",
                   command=self._load_catalog).grid(column=1, row=0, padx=10)

        # insert new frame
        _insert_frame = ttk.LabelFrame(_options_frame,
                                       text="Aggiungi nuovo nome")
        _insert_frame.grid(column=3, row=1, sticky=tk.N)

        ttk.Label(_insert_frame, text="abbr.").grid(column=0, row=1,
                                                    sticky=tk.W)
        self._short_name = ttk.Entry(_insert_frame)
        self._short_name.grid(column=1, row=1)

        ttk.Label(_insert_frame, text="intero").grid(column=0, row=2,
                                                     sticky=tk.W)
        self._long_name = ttk.Entry(_insert_frame)
        self._long_name.grid(column=1, row=2)

        ttk.Label(_insert_frame, text="lang").grid(column=0, row=3,
                                                   sticky=tk.W)
        self._lang_select = ttk.Combobox(_insert_frame, value=["it", "en"],
                                         state="readonly", width=5)
        self._lang_select.grid(column=1, row=3, sticky=tk.W)
        self._lang_select.current(0)

        ttk.Button(_insert_frame, text="Aggiungi",
                   command=self._insert_to_catalog).grid(column=1, row=3,
                                                         sticky=tk.E)

        self._btn_save = ttk.Button(_options_frame, text="Salva modifiche",
                                    state="disabled",
                                    command=self._save_new_catalog)
        self._btn_save.grid(column=3, row=2, pady=15)

        ttk.Button(_options_frame, text="Cancella nome selezionato",
                   command=self._delete_selected).grid(column=3, row=3)

    @property
    def save_button(self):
        """Get save button state."""
        return self._btn_save["state"]

    @save_button.setter
    def save_button(self, value):
        """Set save button state."""
        self._btn_save["state"] = value

    @property
    def _language(self):
        """Return the language selected: it or eng."""
        return self._lang_select.get()

    def _course_name_size(self, course_name):
        """Check if name course is 3 letters long otherwise raise error."""
        if self.get_catalog == "corsi" and not len(course_name) == 3:
            raise ValueError("Course name has to be 3 letters long")

    def _generate_tree_columns(self):
        """Generate columns for the treeview widget."""
        self._tree_list["show"] = "headings"
        self._tree_list.heading('names_short', text='Nome abbreviato')
        self._tree_list.column('names_short', width=150)
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

    def _load_catalog(self):
        """Load name list into treeview widget."""
        self._refresh_list()

        # self._btn_insert["state"] = "active"

        row_colors = ["oddrow", "evenrow"]
        catalog_names = sorted(self._catalog_list[self.get_catalog].items())
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
            messagebox.showinfo(title="Cancella",
                                message="Nessun nome selezionato")
            return
        confirm = messagebox.askyesno(title="Cancella selezione",
                                      message=(f"Cancellare: {selected_item}?")
                                      )
        if confirm:
            self._tree_list.delete(selected_item)
            self._delete_from_catalog(selected_item)
            self.save_button = "active"

    def _delete_from_catalog(self, delete_key):
        """Delete key from class catalog list."""
        # TODO: currently not deleting the file on disk?
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
            self._course_name_size(short_name)
            self._tree_list.insert("", 0, short_name)

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
            self._tree_list.set(short_name, 'names_short', short_name)
            self._tree_list.set(short_name, 'names_long', long_name)

            if self.get_catalog == "docenti":
                self._catalog_list[self.get_catalog].update(
                    {short_name: long_name})

            else:
                self._catalog_list[self.get_catalog].update(
                    {short_name: {"course_name": long_name}})

            self._updated_names[self.get_catalog] = [long_name, self._language]
            self.save_button = "active"

    def _save_new_catalog(self):
        """Save new verison of catalog after delete or added new names."""
        with open(util.catalog_file(), "w") as json_file:
            json.dump(self._catalog_list, json_file, indent=True)
        if self._updated_names:
            self._update_audio_library()
        messagebox.showinfo(title="", message="Modifiche salvate!")

    def _update_audio_library(self):
        """Update audio library with deleting or adding the modifications."""
        for category, list_ in self._updated_names.items():
            name, lang = list_
            file_name = name.replace(" ", "_")
            util.generate_audio_clip(name, file_name,
                                     f"include/audio/{category}", lang)
