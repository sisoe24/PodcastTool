"""Catalog page frame from the gui.

From here you can modify the name catalog by adding and deleting other names.
The module will create the audio files for the newly created names.
"""
import os
import re
import json
import logging
import pathlib

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


from app import CustomDialog
from utils import util, catalog
from startup import USER_AUDIO, APP_GEOMETRY
from utils.resources import _catalog_file

LOGGER = logging.getLogger('podcasttool.widgets.catalogframe')


class AddNewEntry(CustomDialog):
    def __init__(self, title, enable_corsi='disabled', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(title)

        ttk.Label(self._layout, text='Abbrev.').grid(row=0, sticky=tk.E)
        ttk.Label(self._layout, text='Intero').grid(row=1, sticky=tk.E)
        ttk.Label(self._layout, text='Language').grid(row=2, sticky=tk.E)
        ttk.Label(self._layout, text='Corso',
                  state=enable_corsi).grid(row=3, sticky=tk.E)

        self._short_name = ttk.Entry(self._layout, width=24)
        self._long_name = ttk.Entry(self._layout, width=24)
        self._lang_select = ttk.Combobox(self._layout, state="readonly",
                                         value=["it", "en"], width=5)
        self._lang_select.current(0)

        _corsi = ["ALP", "ELM", "EMP", "TTS"]
        self._course = ttk.Combobox(self._layout, value=_corsi,
                                    state=enable_corsi, width=5)

        self._short_name.grid(row=0, column=1)
        self._long_name.grid(row=1, column=1)
        self._lang_select.grid(row=2, column=1, sticky=tk.W)
        self._course.grid(row=3, column=1, sticky=tk.W)

    def clean_name(self, name: str) -> str:

        name = re.sub(r'[^A-zÀ-ÿ_0-9]|\[|\]', '_', name.strip())
        name = re.sub(r'_{2,}', '_', name)

        return name.title()

    def long_name(self):
        return self.clean_name(self._long_name.get())

    def short_name(self):
        return self.clean_name(self._short_name.get())

    def course(self):
        return self._course.get()


class CatalogLoad(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._selected_catalog = ttk.Combobox(self, value=["docenti", "corsi"],
                                              width=10, state="readonly")
        self._selected_catalog.grid(
            column=1, row=0, pady=10, padx=10, sticky=tk.E)

        self._load_btn = ttk.Button(self, text="Carica lista")
        self._load_btn.grid(column=0, row=0)

    @property
    def load_button(self):
        return self._load_btn

    def catalog_selection(self):
        return self._selected_catalog.get()


class CatalogFrame(ttk.Frame):
    # TODO: should be nice to order by selecting the column
    _catalog_list = catalog()

    _updated_names = {"docenti": [], "corsi": []}
    _delete_audio = []

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._load_widget = CatalogLoad(self)
        self._load_widget.grid(column=0, row=0, columnspan=3, padx=10)
        self._load_widget.load_button.config(command=self._load_catalog)

        # TREE VIEW
        self.vertical_scrollbar = ttk.Scrollbar(self)
        self._tree_list = ttk.Treeview(
            self, height=APP_GEOMETRY.treeview_height,
            selectmode='browse', yscrollcommand=self.vertical_scrollbar.set,
            columns=("names_short", "names_long", 'code_course'))

        self._tree_list.grid(column=0, row=1, columnspan=3, rowspan=2,
                             sticky=tk.W + tk.E)

        self.vertical_scrollbar.grid(column=3, row=1, rowspan=2,
                                     sticky=tk.N + tk.S)
        self._generate_tree_columns()
        self.vertical_scrollbar.config(command=self._tree_list.yview)

        # BUTTON SECTION
        ttk.Button(self, text="Aggiungi Docente", command=self._add_docenti).grid(
            column=0, row=3, sticky=tk.W,)

        ttk.Button(self, text="Aggiungi Corso", command=self._add_corso).grid(
            column=0, row=3, padx=100, sticky=tk.E)

        # self._course = None
        ttk.Button(self, text="Cancella Selezione", command=self._delete_selected).grid(
            column=2, row=3, pady=10, sticky=tk.NE)

        self._catalog = None

    def _generate_tree_columns(self):
        """Generate columns for the treeview widget."""
        self._tree_list["show"] = "headings"

        self._tree_list.heading('names_short', text='Nome Abbreviato')
        self._tree_list.column('names_short', width=150)

        self._tree_list.heading('names_long', text='Nome intero')
        self._tree_list.column('names_long', width=290)

        self._tree_list.heading('code_course', text='Codice Corso')
        self._tree_list.column('code_course', width=100)

        self._tree_list.tag_configure("oddrow", background='gray90')
        self._tree_list.tag_configure("evenrow", background='gray99')

    def _refresh_list(self):
        """Refresh (delete) list in treeview widget when loading other list."""
        self._tree_list.delete(*self._tree_list.get_children())

    def _reset_list(self):
        """When loading catalog, reset modification that have not be saved."""
        self._updated_names = {"docenti": [], "corsi": []}
        self._catalog_list = catalog()

    @property
    def _language(self):
        """Return the language selected: it or eng."""
        return self.new_entry._lang_select.get()

    @property
    def catalog(self):
        """Return the catalog name selected from the combobox widget."""
        return self._catalog

    @catalog.setter
    def catalog(self, value):
        self._catalog = value

    def _load_catalog(self):
        """Load name list into treeview widget."""
        self.catalog = self._load_widget.catalog_selection()
        self._reset_list()
        self._refresh_list()

        try:
            catalog_names = sorted(self._catalog_list[self.catalog].items())
        except KeyError:
            return

        for index, names in enumerate(catalog_names):
            # print("➡ names :", names)

            if index % 2 == 0:
                self._tree_list.insert('', index, names[0], tags=('oddrow'))
            else:
                self._tree_list.insert('', index, names[0], tags=('evenrow'))

            self._tree_list.set(names[0], 'names_short', names[0])

            if self.catalog == 'corsi':
                self._tree_list.set(names[0], 'names_long',
                                    names[1]["course_name"])

                self._tree_list.set(names[0], 'code_course',
                                    names[1]["course_path"])
            else:
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
                                      message=(f"Cancellare: {selected_item}?"))
        if confirm:
            item = self._tree_list.item(self._tree_list.selection())
            audio_name = item['values'][1].replace(' ', '_').lower()
            self._delete_audio.append(f'{audio_name}.mp3')

            self._tree_list.delete(selected_item)
            self._delete_from_catalog(selected_item)
            self._save_new_catalog()

    def _delete_from_catalog(self, delete_key):
        """Delete key from class catalog list."""
        self._catalog_list[self.catalog].pop(delete_key)

    def _add_corso(self):
        self.new_entry = AddNewEntry(
            title='Aggiungi Corso', enable_corsi='readonly')
        self.catalog = 'corsi'

        self.new_entry._save_btn.config(command=self._insert_to_catalog)

    def _add_docenti(self):
        self.new_entry = AddNewEntry(title='Aggiungi Docente')
        self.catalog = 'docenti'

        self.new_entry._save_btn.config(command=self._insert_to_catalog)

    def _get_new_names(self):
        """Return a tuple with new names to insert taken from Entry widget.

        Return:
            tuple - short_name and long_name variables.
        """
        short_name = self.new_entry.short_name()
        long_name = self.new_entry.long_name()

        if not short_name or not long_name:
            messagebox.showinfo(title="Errore", message="Nome invalido")
            return None

        if self.catalog == 'corsi':
            short_name = short_name.upper()

        return (short_name, long_name)

    def _check_name_size(self, course_name):
        """Check if name course is 3 letters long otherwise raise error."""
        if self.catalog == "corsi" and not len(course_name) == 3:
            raise ValueError("Course name has to be 3 letters long")

    def _insert_to_catalog(self):
        """Insert new name into treeview widget."""
        short_name, long_name = self._get_new_names()
        try:
            short_name, long_name = self._get_new_names()
            self._check_name_size(short_name)

        except TypeError as error:
            LOGGER.info('type error: %s', error, exc_info=True)
            messagebox.showinfo(title="PodcastTool",
                                message=f"Nessun nome inserito.{error}")

        except tk._tkinter.TclError:
            messagebox.showerror(title="PodcastTool",
                                 message="Nome esiste già!")

        except ValueError:
            messagebox.showerror(
                title="PodcastTool",
                message="Nome del corso dovrebbe avere solo 3 lettere")
        else:
            section = self.catalog
            if section == "docenti":
                self._catalog_list[section].update(
                    {short_name: long_name.replace('_', ' ')})

            elif section == 'corsi':
                course_path = self.new_entry.course()
                if not course_path:
                    messagebox.showerror(message="manca codice corso")
                    return
                self._catalog_list[section].update(
                    {short_name: {"course_name": long_name,
                                  "course_path": course_path}})

            self._updated_names[section].append(
                [long_name, self._language])

            self._save_new_catalog()
            self._updated_names[section].clear()
            self._load_catalog()

    def _save_new_catalog(self):
        """Save new verison of catalog after delete or added new names."""
        with open(_catalog_file(), "w") as json_file:
            json.dump(self._catalog_list, json_file, indent=True)

        self.update()
        self._update_audio_library()

        if self._delete_audio:
            self._delete_new_audio()
            self._delete_audio.clear()

    def _delete_new_audio(self):
        for file in pathlib.Path(USER_AUDIO).glob('*mp3'):
            if file.name in self._delete_audio:
                LOGGER.info('Deleting file: %s', file)
                os.remove(file)

    def _update_audio_library(self):
        """Update audio library with deleting or adding the modifications."""

        report_msg = 'Modifiche salvate!'

        for new_names in self._updated_names.values():
            for new_name in new_names:
                name, lang = new_name

                if util.generate_audio(text=name.lower(), path=USER_AUDIO, lang=lang):
                    report_msg += f"\nAudio Generato per: {name}"
                else:
                    report_msg += f"\nProblemi per: {name}\nControlla log file"

        messagebox.showinfo(title='PodcastTool', message=report_msg)