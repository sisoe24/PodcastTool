import platform

OS_SYSTEM = platform.system()


class AppGeometry:

    @property
    def width(self):
        return 650

    @property
    def height(self):
        return 550

    @property
    def log_width(self):
        return 630

    @property
    def log_height(self):
        return 242

    @property
    def log_font(self):
        default = 15
        if OS_SYSTEM == 'Darwin':
            return default
        return default - 4

    @property
    def textbox_width(self):
        default = 42
        if OS_SYSTEM == 'Darwin':
            return default
        return default + 6

    @property
    def textbox_font(self):
        default = 21
        if OS_SYSTEM == 'Darwin':
            return default
        return default - 6

    @property
    def treeview_height(self):
        return 17

    @property
    def html_font(self):
        default = 21
        if OS_SYSTEM == 'Darwin':
            return default
        return default - 6

    @property
    def dialog_width(self):
        return 320

    @property
    def dialog_height(self):
        return 150
