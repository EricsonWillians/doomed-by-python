import os
import datetime
import struct
import zipfile
from PyQt5.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QPlainTextEdit,
    QApplication,
)
from PyQt5.Qt import Qt


def _wad_details(path: str) -> str:
    info = []
    try:
        with open(path, 'rb') as fh:
            ident = fh.read(4).decode('ascii', 'ignore')
            if ident not in {'IWAD', 'PWAD'}:
                return ''
            num = struct.unpack('<I', fh.read(4))[0]
            offset = struct.unpack('<I', fh.read(4))[0]
            info.append(f'Type: {ident}')
            info.append(f'Lumps: {num}')
            fh.seek(offset)
            for i in range(min(num, 20)):
                pos, size = struct.unpack('<II', fh.read(8))
                name = fh.read(8).decode('ascii', 'ignore').rstrip('\0')
                info.append(f' {i:03d}: {name} ({size} bytes)')
        if num > 20:
            info.append(' ...')
    except OSError:
        pass
    return '\n'.join(info)


def _pk3_details(path: str) -> str:
    info = []
    try:
        with zipfile.ZipFile(path) as zf:
            info.append(f'ZIP entries: {len(zf.infolist())}')
            for zi in zf.infolist()[:20]:
                info.append(f' {zi.filename} ({zi.file_size} bytes)')
            if len(zf.infolist()) > 20:
                info.append(' ...')
    except (OSError, zipfile.BadZipFile):
        pass
    return '\n'.join(info)


def describe(path: str) -> str:
    lines = [f'Path: {path}']
    try:
        stat = os.stat(path)
        lines.append(f'Size: {stat.st_size} bytes')
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
        lines.append(f'Modified: {mtime:%Y-%m-%d %H:%M:%S}')
    except OSError:
        pass
    if path.lower().endswith('.pk3') or zipfile.is_zipfile(path):
        detail = _pk3_details(path)
        if detail:
            lines.append(detail)
    else:
        detail = _wad_details(path)
        if detail:
            lines.append(detail)
    return '\n'.join(lines)


class PWadInfo(QGroupBox):
    """Widget showing detailed information about selected mods."""

    def __init__(self, title='Mod Info'):
        super().__init__(title)
        layout = QVBoxLayout()
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        self.setLayout(layout)

    def showInfo(self, paths):
        """Display information for selected mod paths with a busy cursor."""
        if not paths:
            self.text.clear()
            return

        # Indicate the UI is busy while large mods are parsed
        self.text.setPlainText("Loading...")
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            details = '\n\n'.join(describe(p) for p in paths)
            self.text.setPlainText(details)
        finally:
            QApplication.restoreOverrideCursor()
