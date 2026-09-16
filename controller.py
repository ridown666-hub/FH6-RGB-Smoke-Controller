import ctypes
import hashlib
import json
import os
import re
import shutil
import sys
import stat
import xml.etree.ElementTree as ET
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageEnhance, ImageTk
APP_NAME = 'FH6 RGB Smoke Controller'
APP_VERSION = '5.11.1'

def resource_path(relative):
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base / relative

def data_dir():
    root = Path(os.getenv('LOCALAPPDATA', Path.home())) / 'RicardoStonePT' / 'FH6RGBSmoke'
    root.mkdir(parents=True, exist_ok=True)
    return root
# The fourth DustRGBDepth component controls the amount/depth of the
# replacement particle effect.  0.220 was visible at night but was too weak
# against a bright daytime scene, so this release uses a stronger daytime
# value and a slightly denser trailing haze.  The values stay below the very
# heavy 0.8-1.0 sand presets already shipped in the game's XML.
DAYLIGHT_DUST_DEPTH = 0.55
TRAIL_DUST_DEPTH = 0.65
TRAIL_RANGE = 600
EXHAUST_TARGET = Path('Particles/Textures/fire/swatches')
EXHAUST_COLORS = (
    'blue', 'green', 'pink', 'purple', 'red', 'yellow', 'white', 'orange',
    'cyan', 'lime', 'gold', 'blue_pink', 'red_blue', 'purple_white',
    'green_purple', 'red_white', 'neon_cyan_pink', 'neon_lime_purple',
)
PRESETS = {
    'ORIGINAL': None,
    'AZUL NEON': (0, 170, 255),
    'ROXO ELÉTRICO': (150, 45, 255),
    'ROSA NEON': (255, 30, 155),
    'VERMELHO': (255, 35, 35),
    'LARANJA': (255, 105, 15),
    'VERDE ÁCIDO': (75, 255, 45),
    'CIANO': (0, 255, 225),
    'DOURADO': (255, 190, 25),
    'TURQUESA NEON': (0, 255, 190),
    'MAGENTA NEON': (255, 0, 220),
    'LIMA NEON': (160, 255, 0),
    'AMARELO NEON': (255, 235, 0),
    'ULTRAVIOLETA NEON': (95, 0, 255),
    'RGB': 'rgb',
}

# Experimental static multicolour preset. All three effect names and their
# attributes occur in the supplied TireEffectsDefinitions.xml. Use different
# emitters: repeated entries with the same Name may be collapsed by the game.
# This writes three colour inputs; it does not prove that FH6 renders distinct
# plumes, and does not implement an animated hue cycle or hot reload.
RGB_EFFECTS = (
    ('Surface_Offroad_Master', PRESETS['CIANO'], DAYLIGHT_DUST_DEPTH, ''),
    ('Surface_Dust_Trail', PRESETS['ROSA NEON'], TRAIL_DUST_DEPTH,
     f' Range="{TRAIL_RANGE}" SelfKill="true"'),
    ('Surface_Dust_Debri_Wave', PRESETS['DOURADO'], 0.4, ' Range="30"'),
)

RGB_SELECTION = 'RGB — CIANO · ROSA · DOURADO'
RGB_STATUS = 'RGB APLICADO — TESTA NO JOGO'
RGB_INSTALLED = 'Textura RGB e efeitos multicoloridos aplicados.'
RGB_EXPLANATION = (
    'A textura smoke.dds RGB é instalada juntamente com o perfil XML '
    'ciano/rosa/dourado. Fecha e reabre o FH6 para ele recarregar os dois.'
)

class SmokeController(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        try:
            self.iconbitmap(str(resource_path('assets/app_icon.ico')))
        except tk.TclError:
            pass
        self.geometry('1280x760')
        self.minsize(1050, 680)
        self.configure(bg='#05070e')
        try:
            self.attributes('-alpha', 0.97)
        except tk.TclError:
            pass
        self.selected = 'RGB'
        self.cards = {}
        self.settings_file = data_dir() / 'settings.json'
        self.settings = self.load_settings()
        self.game_root = tk.StringVar(value=self.settings.get('game_root', ''))
        self.status = tk.StringVar(value='PRONTO PARA TRANSFORMAR O FUMO')
        # The GTR artwork is the current default; retain the previous scene
        # as a fallback for older/custom installations.
        # JPEG keeps the GitHub source package compact without changing the
        # visible composition. Older/custom installations can still fall back
        # to the previous PNG name.
        background = resource_path('assets/background_gtr.jpg')
        if not background.exists():
            background = resource_path('assets/background_gtr.png')
        if not background.exists():
            background = resource_path('assets/background.png')
        self._bg_src = Image.open(background).convert('RGB')
        self.bg_label = tk.Label(self, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind('<Configure>', self.resize_background)
        self.after(50, self.build_ui)
        self.after(150, self.auto_detect)

    def resolved_game_root(self):
        """Return the FH6 install root, even when the user picked MediaPC/Content."""
        raw = self.game_root.get().strip().strip('"')
        root = Path(raw) if raw else Path()
        if root.name.lower() in {'mediapc', 'content', 'media'} and root.parent.is_dir():
            parent = root.parent
            # The picker was sometimes pointed at the resource subfolder.  The
            # loose smoke override belongs beside that folder, at the game root.
            if any((parent / marker).exists() for marker in ('forzahorizon6.exe', 'media', 'MediaPC', 'Content')):
                root = parent
                if self.game_root.get().strip() != str(root):
                    self.game_root.set(str(root))
                    self.save_settings()
        return root

    def load_settings(self):
        try:
            return json.loads(self.settings_file.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def save_settings(self):
        self.settings['game_root'] = self.game_root.get()
        self.settings_file.write_text(json.dumps(self.settings, indent=2), encoding='utf-8')

    def resize_background(self, event=None):
        if not self.winfo_width() or not self.winfo_height():
            return
        image = self._bg_src.resize((self.winfo_width(), self.winfo_height()), Image.Resampling.LANCZOS)
        image = ImageEnhance.Brightness(image).enhance(0.64)
        self._bg_photo = ImageTk.PhotoImage(image)
        self.bg_label.configure(image=self._bg_photo)

    def panel(self, parent, **kwargs):
        return tk.Frame(parent, bg=kwargs.pop('bg', '#0a1020'), highlightthickness=1, highlightbackground=kwargs.pop('border', '#213a62'), **kwargs)

    def build_ui(self):
        root = tk.Frame(self, bg='#05070e')
        root.place(relx=0.035, rely=0.055, relwidth=0.93, relheight=0.89)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        side = self.panel(root, bg='#070b14', border='#00c8ff', width=245)
        side.grid(row=0, column=0, sticky='nsw', padx=(0, 12))
        side.grid_propagate(False)
        tk.Label(side, text='FH6', fg='#ffffff', bg='#070b14', font=('Segoe UI Black', 34)).pack(anchor='w', padx=24, pady=(26, 0))
        tk.Label(side, text='RGB SMOKE', fg='#00d9ff', bg='#070b14', font=('Segoe UI Black', 17)).pack(anchor='w', padx=26)
        tk.Label(side, text='CONTROLLER', fg='#cf48ff', bg='#070b14', font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=27, pady=(0, 35))
        for text, cmd in [('◈  CORES DO FUMO', self.show_colors), ('▣  LOCAL DO JOGO', self.choose_folder), ('↺  RESTAURAR ORIGINAL', self.restore_original), ('▶  EXECUTAR FH6', self.launch_game), ('ⓘ  SOBRE', self.show_about)]:
            b = tk.Button(side, text=text, command=cmd, anchor='w', relief='flat', bd=0, bg='#0b1322', activebackground='#132944', fg='#e9f8ff', activeforeground='#00ddff', font=('Segoe UI', 10, 'bold'), cursor='hand2')
            b.pack(fill='x', padx=15, pady=5, ipady=12)
            b.bind('<Enter>', lambda e, w=b: w.configure(bg='#152945', fg='#62edff'))
            b.bind('<Leave>', lambda e, w=b: w.configure(bg='#0b1322', fg='#e9f8ff'))
        tk.Label(side, text='RICARDOSTONEPT  •  v' + APP_VERSION, fg='#536a84', bg='#070b14', font=('Segoe UI', 8, 'bold')).pack(side='bottom', pady=20)
        main = self.panel(root, bg='#08101d', border='#bc39ff')
        main.grid(row=0, column=1, sticky='nsew')
        header = tk.Frame(main, bg='#08101d')
        header.pack(fill='x', padx=26, pady=(22, 8))
        tk.Label(header, text='ESCOLHE A COR DO DRIFT', fg='white', bg='#08101d', font=('Segoe UI Black', 24)).pack(anchor='w')
        tk.Label(header, text='Seleciona uma cor e carrega em APLICAR NO JOGO.', fg='#8da9c5', bg='#08101d', font=('Segoe UI', 10)).pack(anchor='w', pady=(2, 0))
        grid = tk.Frame(main, bg='#08101d')
        grid.pack(fill='both', expand=True, padx=26, pady=10)
        for c in range(3):
            grid.grid_columnconfigure(c, weight=1)
        for i, (name, color) in enumerate(PRESETS.items()):
            row, col = divmod(i, 3)
            card = tk.Frame(grid, bg='#101a2a', highlightthickness=2, highlightbackground='#1d3048', cursor='hand2')
            card.grid(row=row, column=col, sticky='nsew', padx=7, pady=7, ipady=6)
            card.bind('<Button-1>', lambda e, n=name: self.select(n))
            swatch = tk.Canvas(card, width=54, height=54, bg='#101a2a', highlightthickness=0)
            swatch.pack(side='left', padx=12, pady=8)
            if color == 'rgb':
                for x, fill in enumerate(('#00d9ff', '#853cff', '#ff239d', '#ff392f', '#79ff31')):
                    swatch.create_rectangle(x * 11, 0, x * 11 + 12, 54, fill=fill, outline='')
            else:
                fill = '#d8dde4' if color is None else '#%02x%02x%02x' % color
                swatch.create_oval(4, 4, 50, 50, fill=fill, outline='#ffffff', width=2)
            lab = tk.Label(card, text=name, fg='#eef9ff', bg='#101a2a', font=('Segoe UI', 10, 'bold'))
            lab.pack(side='left', padx=2)
            lab.bind('<Button-1>', lambda e, n=name: self.select(n))
            pick = tk.Button(card, text='ESCOLHER', command=lambda n=name: self.select(n), bg='#182a41', fg='#9edfff', activebackground='#00bce8', activeforeground='#00101a', relief='flat', bd=0, font=('Segoe UI', 7, 'bold'), cursor='hand2')
            pick.pack(side='right', padx=10, ipadx=5, ipady=4)
            self.cards[name] = card
        pathbar = tk.Frame(main, bg='#08101d')
        pathbar.pack(fill='x', padx=32, pady=(2, 6))
        tk.Label(pathbar, text='PASTA FH6', fg='#7792ac', bg='#08101d', font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        entry = tk.Entry(pathbar, textvariable=self.game_root, bg='#050a12', fg='#d8eeff', insertbackground='white', relief='flat', font=('Segoe UI', 9))
        entry.pack(side='left', fill='x', expand=True, ipady=8)
        tk.Button(pathbar, text='PROCURAR', command=self.choose_folder, bg='#172b43', fg='white', activebackground='#214563', relief='flat', bd=0, font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side='right', padx=(8, 0), ipady=8, ipadx=10)
        actions = tk.Frame(main, bg='#08101d')
        actions.pack(fill='x', padx=32, pady=(4, 20))
        tk.Label(actions, textvariable=self.status, fg='#57eaff', bg='#08101d', font=('Segoe UI', 9, 'bold')).pack(side='left')
        tk.Button(actions, text='APLICAR NO JOGO', command=self.apply_selected, bg='#00bce8', fg='#00101a', activebackground='#7c40ff', activeforeground='white', relief='flat', bd=0, font=('Segoe UI Black', 11), cursor='hand2').pack(side='right', ipadx=24, ipady=11)
        self.select(self.selected)

    def show_colors(self):
        self.status.set('ESCOLHE UMA COR E CARREGA EM APLICAR NO JOGO')

    def show_about(self):
        win = tk.Toplevel(self)
        win.title('Sobre — ' + APP_NAME)
        win.geometry('650x500')
        win.resizable(False, False)
        win.configure(bg='#070b14')
        win.transient(self)
        win.grab_set()
        try:
            win.attributes('-alpha', 0.98)
        except tk.TclError:
            pass
        shell = tk.Frame(win, bg='#091321', highlightthickness=2, highlightbackground='#a83dff')
        shell.pack(fill='both', expand=True, padx=18, pady=18)
        tk.Label(shell, text='FH6', fg='white', bg='#091321', font=('Segoe UI Black', 38)).pack(pady=(26, 0))
        tk.Label(shell, text='RGB SMOKE CONTROLLER', fg='#28dcff', bg='#091321', font=('Segoe UI Black', 18)).pack()
        tk.Label(shell, text='VERSÃO ' + APP_VERSION, fg='#d34cff', bg='#091321', font=('Segoe UI', 9, 'bold')).pack(pady=(3, 20))
        info = 'Interface de seleção e instalação do efeito de fumo.\nAs cores usam o efeito de poeira colorida do motor do FH6.\n\nCOMO FUNCIONA\n1. Fecha o jogo.\n2. Escolhe a pasta principal do FH6.\n3. Seleciona uma cor de fumo.\n4. Carrega em APLICAR NO JOGO.\n5. Abre o FH6 pela aplicação.\n\nAntes da primeira alteração é criada uma cópia de segurança. O botão RESTAURAR ORIGINAL recupera o ficheiro anterior.'
        tk.Label(shell, text=info, justify='left', wraplength=540, fg='#c5d8eb', bg='#091321', font=('Segoe UI', 10), padx=25).pack(fill='x')
        tk.Label(shell, text='CRIADO PARA RICARDOSTONEPT', fg='#708ca8', bg='#091321', font=('Segoe UI', 8, 'bold')).pack(side='bottom', pady=(0, 14))
        tk.Button(shell, text='FECHAR', command=win.destroy, bg='#b33cff', fg='white', activebackground='#28dcff', activeforeground='#00101a', relief='flat', bd=0, font=('Segoe UI Black', 10), cursor='hand2').pack(side='bottom', ipadx=35, ipady=8, pady=14)

    def select(self, name):
        self.selected = name
        for n, card in self.cards.items():
            card.configure(highlightbackground='#00e7ff' if n == name else '#1d3048', bg='#142742' if n == name else '#101a2a')
            for child in card.winfo_children():
                if isinstance(child, (tk.Label, tk.Canvas)):
                    child.configure(bg='#142742' if n == name else '#101a2a')
        self.status.set('SELECIONADO: ' + name)

    def candidate_roots(self):
        roots = []
        if self.game_root.get():
            roots.append(Path(self.game_root.get()))
        for drive in 'CDEFG':
            roots += [Path(f'{drive}:/Program Files (x86)/Steam/steamapps/common/Forza Horizon 6'), Path(f'{drive}:/SteamLibrary/steamapps/common/Forza Horizon 6'), Path(f'{drive}:/Games/Steam/steamapps/common/Forza Horizon 6')]
        return roots

    def auto_detect(self):
        if self.game_root.get() and Path(self.game_root.get()).exists():
            return
        for root in self.candidate_roots():
            if root.exists():
                self.game_root.set(str(root))
                self.save_settings()
                self.status.set('FH6 DETETADO AUTOMATICAMENTE')
                return

    def choose_folder(self):
        chosen = filedialog.askdirectory(title=self.tr('Seleciona a pasta principal do Forza Horizon 6'))
        if chosen:
            self.game_root.set(chosen)
            self.save_settings()
            self.status.set('PASTA DO JOGO GUARDADA')

    def smoke_targets(self):
        root = self.resolved_game_root()
        # The documented FH6 loose override is media\\Tracks\\Brio\\smoke.dds.
        # Keep legacy Content/MediaPC locations for older installs/mod loaders.
        candidates = [
            root / 'media/Tracks/Brio/smoke.dds',
            root / 'Media/Tracks/Brio/smoke.dds',
            root / 'Content/media/Tracks/Brio/smoke.dds',
            root / 'Content/mediapc/Tracks/Brio/smoke.dds',
            root / 'mediapc/Tracks/Brio/smoke.dds',
        ]
        # Windows treats `media` and `Media` as the same directory.  Deduplicate
        # by normalized absolute path so the confirmation reports one target.
        existing = self.unique_paths([p for p in candidates if p.exists()])
        if existing:
            return existing
        try:
            found = self.unique_paths([p for p in root.rglob('smoke.dds') if p.is_file()])
            if found:
                return found
        except (OSError, PermissionError):
            pass
        # The original game asset is usually packed, so no loose smoke.dds may
        # exist yet.  Creating this exact path is the intended mod override.
        return [root / 'media/Tracks/Brio/smoke.dds']

    def unique_paths(self, paths):
        """Deduplicate paths on Windows, where media and Media are identical."""
        result, seen = [], set()
        for path in paths:
            key = os.path.normcase(str(path.resolve(strict=False))).casefold()
            if key not in seen:
                seen.add(key)
                result.append(path)
        return result

    def physics_targets(self):
        """Return the loose FH6 physics XML target used by tire effects."""
        root = self.resolved_game_root()
        candidates = [
            root / 'media/Physics/TireEffectsDefinitions.xml',
            root / 'Media/Physics/TireEffectsDefinitions.xml',
            root / 'Content/media/Physics/TireEffectsDefinitions.xml',
            root / 'Content/mediapc/Physics/TireEffectsDefinitions.xml',
            root / 'mediapc/Physics/TireEffectsDefinitions.xml',
        ]
        existing = self.unique_paths([p for p in candidates if p.exists()])
        if existing:
            return existing
        try:
            found = self.unique_paths([p for p in root.rglob('TireEffectsDefinitions.xml') if p.is_file()])
            if found:
                return found
        except (OSError, PermissionError):
            pass
        return [root / 'media/Physics/TireEffectsDefinitions.xml']

    def exhaust_media_root(self):
        """Resolve the loose MediaPC root used by FH6 exhaust swatches.

        Nexus-style FH6 mods use a ``MediaPC`` folder beside the game
        executable.  Some installations spell it ``mediapc`` or place it
        below ``Content``; existing folders win, otherwise the conventional
        root/MediaPC overlay is created when the user applies a colour.
        """
        # A directly selected MediaPC is authoritative; never append it twice.
        raw = self.settings.get('exhaust_root', '').strip().strip('"')
        if raw and Path(raw).name.casefold() == 'mediapc':
            return Path(raw)
        root = self.resolved_exhaust_root()
        candidates = [
            root / 'MediaPC',
            root / 'mediapc',
            root / 'Content/MediaPC',
            root / 'Content/mediapc',
        ]
        existing = self.unique_paths([p for p in candidates if p.is_dir()])
        if existing:
            return existing[0]
        try:
            found = self.unique_paths([
                p for p in root.rglob('*')
                if p.is_dir() and p.name.casefold() == 'mediapc'
            ])
            if found:
                return found[0]
        except (OSError, PermissionError):
            pass
        return root / 'MediaPC'

    def resolved_exhaust_root(self):
        raw = self.settings.get('exhaust_root', '').strip().strip('"')
        if not raw:
            return self.resolved_game_root()
        root = Path(raw)
        if root.name.casefold() == 'mediapc':
            root = root.parent
        return root

    def exhaust_source_dir(self, name):
        """Return the bundled MediaPC tree for one exhaust colour."""
        if name not in EXHAUST_COLORS:
            raise ValueError(f'Cor de escape inválida: {name}')
        source = resource_path('assets/exhaust_colors') / name / 'mediapc'
        if not source.is_dir():
            raise FileNotFoundError(source)
        return source

    def exhaust_backup_root(self, root):
        """Use a stable per-install backup folder for exhaust swatches."""
        key = str(root.resolve(strict=False)).casefold().encode('utf-8', 'replace')
        digest = hashlib.sha1(key).hexdigest()[:16]
        return data_dir() / 'backup' / 'exhaust_original' / digest

    def exhaust_state_file(self):
        return data_dir() / 'backup' / 'exhaust_state.json'

    def load_exhaust_state(self):
        try:
            value = json.loads(self.exhaust_state_file().read_text(encoding='utf-8'))
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def save_exhaust_state(self, state):
        path = self.exhaust_state_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding='utf-8')

    def _exhaust_install_entry(self, root, create=True):
        """Return the state entry for the current game root."""
        state = self.load_exhaust_state()
        roots = state.setdefault('roots', {})
        root_path = str(root.resolve(strict=False))
        root_key = root_path.casefold()
        entry = roots.setdefault(root_key, {'root': root_path, 'files': {}})
        if create:
            entry.setdefault('root', root_path)
            entry.setdefault('files', {})
        return state, entry

    def apply_exhaust_color(self, name):
        """Install one bundled exhaust/backfire colour with automatic backup.

        The user-selected colour pack is copied as a complete MediaPC tree,
        preserving the original six ``.swatchbin`` files and their names.  A
        per-install state file makes switching colours safe and lets the
        existing RESTAURAR ORIGINAL action undo both smoke and exhaust mods.
        """
        source_root = self.exhaust_source_dir(name)
        root = self.resolved_exhaust_root()
        if not root.is_dir() or (not self.settings.get('exhaust_root') and not self.game_root.get().strip()):
            raise ValueError('Seleciona primeiro a pasta do escape.')
        media_root = self.exhaust_media_root()
        target_root = media_root / EXHAUST_TARGET
        source_files = [p for p in source_root.rglob('*') if p.is_file()]
        if not source_files:
            raise FileNotFoundError(f'Não encontrei ficheiros para a cor de escape {name}.')
        state, entry = self._exhaust_install_entry(root)
        backup_root = self.exhaust_backup_root(root)
        installed = []
        for source in source_files:
            relative = source.relative_to(source_root)
            target = media_root / relative
            rel_root = str(target.relative_to(root)).replace('\\', '/')
            backup = backup_root / relative
            meta = entry['files'].setdefault(rel_root, {})
            target.parent.mkdir(parents=True, exist_ok=True)
            # Do not snapshot an overlay created by an earlier colour choice.
            # The first install records whether the file existed; later colour
            # changes must keep that original state instead of backing up the
            # already-modified swatch.
            tracked_before = 'had_loose_file' in meta
            if target.exists() and not backup.exists() and not tracked_before:
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
                meta['had_loose_file'] = True
            elif not target.exists():
                meta.setdefault('had_loose_file', False)
            meta['backup'] = str(backup)
            try:
                os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
            shutil.copy2(source, target)
            if target.stat().st_size != source.stat().st_size:
                raise IOError(f'validação falhou ao copiar: {target}')
            installed.append(target)
        entry['selected'] = name
        entry['target_root'] = str(media_root)
        self.save_exhaust_state(state)
        if len(installed) != 6:
            raise IOError(f'pack de escape incompleto: esperava 6 ficheiros, encontrei {len(installed)}')
        return installed

    def restore_exhaust_original(self, root=None):
        """Restore or remove the current install's exhaust overlay."""
        root = root or self.resolved_exhaust_root()
        state, entry = self._exhaust_install_entry(root, create=False)
        files = entry.get('files', {}) if isinstance(entry, dict) else {}
        restored = 0
        for rel_root, meta in files.items():
            target = root / rel_root
            backup_value = meta.get('backup') if isinstance(meta, dict) else None
            backup = Path(backup_value) if backup_value else self.exhaust_backup_root(root) / Path(rel_root)
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
                shutil.copy2(backup, target)
                restored += 1
            elif isinstance(meta, dict) and meta.get('had_loose_file') is False and target.exists():
                target.unlink()
                restored += 1
        if isinstance(entry, dict):
            entry['files'] = {}
            entry.pop('selected', None)
        self.save_exhaust_state(state)
        return restored

    def ensure_valid_root(self):
        root = self.resolved_game_root()
        if not self.game_root.get().strip() or not root.is_dir():
            messagebox.showerror(APP_NAME, self.tr('Seleciona primeiro a pasta principal do Forza Horizon 6.'))
            return False
        return True

    def preset_file(self, name):
        if name == 'ORIGINAL':
            return resource_path('assets/original/smoke.dds')
        return resource_path('assets/presets') / (name.lower().replace(' ', '_').replace('é', 'e').replace('á', 'a') + '.dds')

    def physics_variant(self, base_text, name):
        """Replace FH6's white tire smoke with a colored, day-visible effect.

        The proven FH5 colored-smoke approach swaps Surface_Smoke for
        Surface_Offroad_Master and supplies DustRGBDepth.  FH6's XML exposes
        the same effect family, while Surface_Smoke itself has no RGB field.
        A Surface_Dust_Trail companion is enabled as well so the haze remains
        visible after the tyre effect is emitted instead of disappearing in
        bright daytime lighting.
        """
        color = PRESETS.get(name)
        if name == 'RGB':
            layers = RGB_EFFECTS
        elif isinstance(color, tuple):
            layers = (
                ('Surface_Offroad_Master', color, DAYLIGHT_DUST_DEPTH, ''),
                ('Surface_Dust_Trail', color, TRAIL_DUST_DEPTH,
                 f' Range="{TRAIL_RANGE}" SelfKill="true"'),
            )
        else:
            raise ValueError(f'Cor de fumo inválida: {name}')
        effects = []
        for effect, channels, depth, attributes in layers:
            rgb = ', '.join(f'{channel / 255.0:.3f}' for channel in channels)
            effects.append(
                f'<Effect Name="{effect}"{attributes}>\n'
                f'                <Attribute Name="DustRGBDepth" Type="vec4" Value="{rgb}, {depth:.3f}" />\n'
                '            </Effect>'
            )
        replacement = '\n            '.join(effects)
        pattern = re.compile(
            r'<Effect\s+Name="Surface_Smoke"\s+'
            r'MinTyreTemperatureForSmoke="[^"]+"\s*/>'
        )
        patched, count = pattern.subn(replacement, base_text)
        if count == 0:
            raise ValueError('Não encontrei o efeito Surface_Smoke no TireEffectsDefinitions.xml.')
        # Reject malformed source/output before replacing an installed file.
        ET.fromstring(patched)
        return patched, count

    def backup_for(self, target, root, state):
        """Create one backup for a target and record whether it was loose."""
        target.parent.mkdir(parents=True, exist_ok=True)
        rel = str(target.relative_to(root)).replace('\\', '/')
        backup = data_dir() / 'backup' / target.relative_to(root)
        # When the first install created a loose overlay, state records
        # had_loose_file=False.  Do not back up that already-coloured overlay
        # when the user selects a second colour; the bundled/original XML is
        # still the clean base in that case.
        if target.exists() and not backup.exists() and rel not in state:
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
            state[rel] = {'had_loose_file': True}
        elif not target.exists():
            state.setdefault(rel, {'had_loose_file': False})
        if target.exists():
            try:
                os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        return rel, backup

    def base_physics_text(self, backup):
        """Use the first backup as the clean base for later color changes."""
        source = backup if backup.exists() else resource_path('assets/original/TireEffectsDefinitions.xml')
        if not source.exists():
            raise FileNotFoundError(source)
        return source.read_text(encoding='utf-8')

    def apply_selected(self):
        if not self.ensure_valid_root():
            return
        if self.selected == 'ORIGINAL':
            return self.restore_original()
        try:
            root = self.resolved_game_root()
            state = self.load_overlay_state()
            targets = self.physics_targets()
            installed = []
            replaced_total = 0
            prepared = []
            # Prepare every target before backup/write so invalid input cannot
            # partially apply a preset or create an unrecorded original backup.
            for target in targets:
                backup = data_dir() / 'backup' / target.relative_to(root)
                if target.exists() and not backup.exists() and str(target.relative_to(root)).replace('\\', '/') not in state:
                    base_text = target.read_text(encoding='utf-8')
                else:
                    base_text = self.base_physics_text(backup)
                patched, replaced = self.physics_variant(base_text, self.selected)
                prepared.append((target, patched, replaced))
            for target, patched, replaced in prepared:
                self.backup_for(target, root, state)
                target.write_text(patched, encoding='utf-8', newline='')
                check = target.read_text(encoding='utf-8')
                if (check != patched or 'DustRGBDepth' not in check or
                        'Surface_Offroad_Master' not in check or
                        'Surface_Dust_Trail' not in check):
                    raise IOError(f'validação falhou: {target}')
                installed.append(target)
                replaced_total += replaced
            # The XML controls the particle tint, but the RGB profile also
            # needs its multicolour texture in the loose FH6 override path.
            # Older builds only wrote the XML, so FH6 kept loading the packed
            # white smoke texture.  Install the DDS with the same backup and
            # restore rules as the physics file.
            texture_installed = []
            if self.selected == 'RGB':
                source = self.preset_file('RGB')
                if not source.exists():
                    raise FileNotFoundError(f'Textura RGB não encontrada: {source}')
                for target in self.smoke_targets():
                    self.backup_for(target, root, state)
                    target.write_bytes(source.read_bytes())
                    if target.read_bytes() != source.read_bytes():
                        raise IOError(f'validação falhou: {target}')
                    texture_installed.append(target)
            self.save_overlay_state(state)
            shown = '\n'.join(str(p) for p in installed + texture_installed)
            if self.selected == 'RGB':
                self.status.set(self.tr(RGB_STATUS))
                messagebox.showinfo(APP_NAME,
                    self.tr(RGB_INSTALLED) + '\n\n' + self.tr(RGB_EXPLANATION) +
                    '\n\n' + shown + '\n\n' + self.tr('Fecha e volta a abrir o FH6 para carregar o efeito.'))
                return
            self.status.set(f'✓ {self.selected} INSTALADO DIA/NOITE — REINICIA O JOGO')
            messagebox.showinfo(APP_NAME, self.tr(
                f'Fumo {self.selected} instalado para dia/noite em '
                f'{len(installed)} ficheiro(s)!\n\n'
                f'Substituições Surface_Smoke: {replaced_total}\n'
                f'Profundidade diurna: {DAYLIGHT_DUST_DEPTH:.3f}  •  Rasto: {TRAIL_RANGE}\n\n'
                f'Ficheiro usado:\n{shown}\n\n'
                'Fecha e volta a abrir o FH6 para carregar o efeito.'
            ))
        except PermissionError:
            messagebox.showerror(APP_NAME, self.tr(
                'O Windows bloqueou a escrita. Fecha o FH6. Se aparecer "Acesso a '
                'pasta protegida", permite apenas este EXE verificado em Segurança '
                'do Windows > Proteção contra ransomware. Não é necessário executar '
                'como administrador nem desligar o Defender.'
            ))
        except Exception as exc:
            messagebox.showerror(APP_NAME, self.tr(f'Não foi possível aplicar o fumo:\n{exc}'))

    def restore_original(self):
        if not self.ensure_valid_root():
            return
        try:
            root = self.resolved_game_root()
            state = self.load_overlay_state()
            restored = 0
            targets = self.unique_paths(self.smoke_targets() + self.physics_targets())
            for target in targets:
                rel = str(target.relative_to(root)).replace('\\', '/')
                backup = data_dir() / 'backup' / target.relative_to(root)
                if backup.exists():
                    try:
                        os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
                    except OSError:
                        pass
                    shutil.copy2(backup, target)
                    restored += 1
                elif state.get(rel, {}).get('had_loose_file') is False and target.exists():
                    # There was no loose file before the mod; remove the
                    # overlay so the packed original is used again.
                    target.unlink()
                    restored += 1
            self.save_overlay_state({k: v for k, v in state.items() if any(str(p.relative_to(root)).replace('\\', '/') == k for p in targets) is False})
            exhaust_restored = self.restore_exhaust_original()
            total_restored = restored + exhaust_restored
            self.status.set('✓ EFEITOS ORIGINAIS RESTAURADOS')
            messagebox.showinfo(APP_NAME, self.tr(
                f'Efeitos originais restaurados ({total_restored} ficheiro(s)).\n'
                f'Fumo: {restored}  •  Escape: {exhaust_restored}\n\n'
                'Reinicia o jogo.'
            ))
        except Exception as exc:
            messagebox.showerror(APP_NAME, self.tr(f'Erro ao restaurar:\n{exc}'))

    def overlay_state_file(self):
        return data_dir() / 'backup' / 'overlay_state.json'

    def load_overlay_state(self):
        try:
            return json.loads(self.overlay_state_file().read_text(encoding='utf-8'))
        except Exception:
            return {}

    def save_overlay_state(self, state):
        path = self.overlay_state_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2), encoding='utf-8')

    def launch_game(self):
        try:
            if sys.platform != 'win32':
                raise OSError('O arranque do FH6 está disponível no Windows.')
            os.startfile('steam://rungameid/2483190')
        except Exception as exc:
            messagebox.showerror(APP_NAME, self.tr(f'Não foi possível abrir o FH6 pelo Steam:\n{exc}'))
if __name__ == '__main__':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    SmokeController().mainloop()
