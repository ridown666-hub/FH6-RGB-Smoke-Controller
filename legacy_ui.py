import tkinter as tk
import ctypes
import sys
import json
import os
from tkinter import filedialog, messagebox
import startup
from ctypes import wintypes
from PIL import Image, ImageTk
from controller import SmokeController, resource_path, PRESETS, EXHAUST_COLORS, APP_NAME, APP_VERSION

EXHAUST_LABELS = {
    'pt': {'blue':'AZUL','green':'VERDE','pink':'ROSA','purple':'ROXO','red':'VERMELHO','yellow':'AMARELO','white':'BRANCO','orange':'LARANJA','cyan':'CIANO','lime':'LIMA','gold':'DOURADO','blue_pink':'AZUL + ROSA','red_blue':'VERMELHO + AZUL','purple_white':'ROXO + BRANCO','green_purple':'VERDE + ROXO','red_white':'VERMELHO + BRANCO','neon_cyan_pink':'CIANO NEON + ROSA','neon_lime_purple':'LIMA NEON + ROXO'},
    'en': {'blue':'BLUE','green':'GREEN','pink':'PINK','purple':'PURPLE','red':'RED','yellow':'YELLOW','white':'WHITE','orange':'ORANGE','cyan':'CYAN','lime':'LIME','gold':'GOLD','blue_pink':'BLUE + PINK','red_blue':'RED + BLUE','purple_white':'PURPLE + WHITE','green_purple':'GREEN + PURPLE','red_white':'RED + WHITE','neon_cyan_pink':'NEON CYAN + PINK','neon_lime_purple':'NEON LIME + PURPLE'},
    'es': {'blue':'AZUL','green':'VERDE','pink':'ROSA','purple':'MORADO','red':'ROJO','yellow':'AMARILLO','white':'BLANCO','orange':'NARANJA','cyan':'CIAN','lime':'LIMA','gold':'DORADO','blue_pink':'AZUL + ROSA','red_blue':'ROJO + AZUL','purple_white':'MORADO + BLANCO','green_purple':'VERDE + MORADO','red_white':'ROJO + BLANCO','neon_cyan_pink':'CIAN NEÓN + ROSA','neon_lime_purple':'LIMA NEÓN + MORADO'},
    'de': {'blue':'BLAU','green':'GRÜN','pink':'ROSA','purple':'LILA','red':'ROT','yellow':'GELB','white':'WEISS','orange':'ORANGE','cyan':'CYAN','lime':'LIMETTE','gold':'GOLD','blue_pink':'BLAU + ROSA','red_blue':'ROT + BLAU','purple_white':'LILA + WEISS','green_purple':'GRÜN + LILA','red_white':'ROT + WEISS','neon_cyan_pink':'NEON-CYAN + ROSA','neon_lime_purple':'NEON-LIMETTE + LILA'},
}
EXHAUST_BORDER = {'blue':'#16AFFF','green':'#28FF70','pink':'#FF47D4','purple':'#A84FFF','red':'#FF3D55','yellow':'#FFD63D','white':'#E8F2FF','orange':'#FF841B','cyan':'#26E5FF','lime':'#68FF2C','gold':'#FFC11A','blue_pink':'#6DC8FF','red_blue':'#FF5070','purple_white':'#C56DFF','green_purple':'#53FF8B','red_white':'#FF6678','neon_cyan_pink':'#00F0FF','neon_lime_purple':'#B7FF3C'}
EXHAUST_UI = {
    'pt': {'title':'CORES DO ESCAPE / BACKFIRE','tab_short':'ESCAPE / BACKFIRE','sub':'18 cores neon simples e duplas; aplica os ficheiros .swatchbin do FH6.','tab':'←  CORES DO FUMO','apply':'APLICAR ESCAPE','ready':'PRONTO A APLICAR'},
    'en': {'title':'EXHAUST / BACKFIRE COLOURS','tab_short':'EXHAUST / BACKFIRE','sub':'18 neon single and dual colours; applies the FH6 .swatchbin files.','tab':'←  TIRE SMOKE','apply':'APPLY EXHAUST','ready':'READY TO APPLY'},
    'es': {'title':'COLORES DEL ESCAPE / BACKFIRE','tab_short':'ESCAPE / BACKFIRE','sub':'18 colores neón simples y dobles; aplica los archivos .swatchbin de FH6.','tab':'←  HUMO DE NEUMÁTICOS','apply':'APLICAR ESCAPE','ready':'LISTO PARA APLICAR'},
    'de': {'title':'AUSPUFF- / BACKFIRE-FARBEN','tab_short':'AUSPUFF / BACKFIRE','sub':'18 einzelne und doppelte Neonfarben; wendet FH6-.swatchbin-Dateien an.','tab':'←  REIFENRAUCH','apply':'AUSPUFF ANWENDEN','ready':'BEREIT ZUM ANWENDEN'},
}
EXHAUST_LABELS['fr'] = {'blue':'BLEU','green':'VERT','pink':'ROSE','purple':'VIOLET','red':'ROUGE','yellow':'JAUNE','white':'BLANC','orange':'ORANGE','cyan':'CYAN','lime':'LIME','gold':'OR','blue_pink':'BLEU + ROSE','red_blue':'ROUGE + BLEU','purple_white':'VIOLET + BLANC','green_purple':'VERT + VIOLET','red_white':'ROUGE + BLANC','neon_cyan_pink':'CYAN NÉON + ROSE','neon_lime_purple':'LIME NÉON + VIOLET'}
EXHAUST_UI['fr'] = {'title':'COULEURS D’ÉCHAPPEMENT / BACKFIRE','tab_short':'ÉCHAPPEMENT / BACKFIRE','sub':'18 couleurs néon simples et doubles ; applique les fichiers .swatchbin de FH6.','tab':'←  FUMÉE DES PNEUS','apply':'APPLIQUER ÉCHAPPEMENT','ready':'PRÊT À APPLIQUER'}

class GamerApp(SmokeController):
    """Interactive image skin with live controls, scaled from reference coordinates."""
    def __init__(self):
        super().__init__()
        self.title(f'FH6 RGB Smoke Controller — {APP_VERSION}')
        self.geometry('1400x788')
        self.minsize(1003,565)
        self.unbind('<Configure>')
        # The live app draws one continuous GTR scene. Keep the legacy field
        # for compatibility with old helper methods, but do not load the old
        # composite artwork (it contained a second photograph underneath).
        self.skin = self._bg_src.copy()
        self.hover = None
        self.focus_index = -1
        self.resize_job = None
        self.drag_origin = None
        self.page = 'colors'
        self.visual_cache = {}
        self.exhaust_path = tk.StringVar(value=self.settings.get('exhaust_root', self.game_root.get()))
        self.startup_note = ''
        self.exhaust_selected = self.settings.get('exhaust_color', 'blue')
        if self.exhaust_selected not in EXHAUST_COLORS:
            self.exhaust_selected = 'blue'
        self.language = self.settings.get('language', 'pt')
        if self.language not in ('pt','en','es','fr','de'):self.language='pt'
        self.translations=json.loads(resource_path('translations.json').read_text(encoding='utf-8'))
        self.render_size = None
        self.exhaust_card_cache = {}
        self.bind('<Map>', self.on_map, add='+')
        self.after(0, self.remove_native_caption)

    def build_ui(self):
        self.bg_label.destroy()
        self.canvas = tk.Canvas(self, bg='#030913', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.path_entry = tk.Entry(self.canvas, textvariable=self.game_root, bg='#06101b',
                                   fg='#d4e8f5', insertbackground='white', relief='flat', bd=0)
        self.path_entry.bind('<FocusOut>', lambda e:self.save_settings())
        self.folder_entry = tk.Entry(self.canvas, bg='#06101b', fg='#d4e8f5', insertbackground='white', relief='flat')
        self.regions = [
            ((35,157,305,232), self.show_colors),
            ((35,251,305,320), lambda:self.change_page('folders')),
            ((35,341,305,410), self.restore_original),
            ((35,432,305,501), self.launch_game),
            ((35,522,305,591), self.show_about)]
        self.smoke_indices = {}
        for i,name in enumerate(PRESETS):
            row,col=divmod(i,5)
            x=351+col*256; y=528+row*124
            idx=len(self.regions)
            self.smoke_indices[name]=idx
            self.regions.append(((x,y,x+240,y+110),lambda n=name:self.select(n)))
        self.exhaust_tab_index=len(self.regions)
        self.regions.append(((1170,447,1614,505),self.toggle_exhaust_page))
        self.browse_index=len(self.regions)
        self.regions.append(((963,832,1126,882),self.choose_folder))
        self.apply_index=len(self.regions)
        self.regions.append(((1247,798,1614,854),self.apply_current))
        self.min_index=len(self.regions)
        self.regions.append(((1500,38,1540,73),self.iconify))
        self.max_index=len(self.regions)
        self.regions.append(((1548,38,1588,73),self.toggle_max))
        self.close_index=len(self.regions)
        self.regions.append(((1599,38,1640,73),self.destroy))
        self.language_index=len(self.regions)
        self.regions.append(((35,637,305,699),lambda:self.change_page('language')))
        self.language_region_start=len(self.regions)
        for i,code in enumerate(('pt','en','es','fr','de')):
            self.regions.append(((390,303+i*131,1575,414+i*131),lambda c=code:self.set_language(c)))
        self.close_panel_index=len(self.regions)
        self.regions.append(((1564,161,1614,211),self.show_colors))
        self.exhaust_indices={}
        for i,name in enumerate(EXHAUST_COLORS):
            row,col=divmod(i,4)
            x=351+col*320; y=360+row*104
            idx=len(self.regions)
            self.exhaust_indices[name]=idx
            self.regions.append(((x,y,x+300,y+96),lambda n=name:self.select_exhaust(n)))
        self.extra={}
        for key,box,action in [
            ('startup',(35,722,305,780),lambda:self.change_page('startup')),
            ('smoke_folder',(390,315,970,440),lambda:self.change_page('smoke_folder')),
            ('exhaust_folder',(995,315,1575,440),lambda:self.change_page('exhaust_folder')),
            ('pick_folder',(1260,390,1550,450),self.pick_module_folder),
            ('save_folder',(1100,510,1550,580),self.save_module_folder),
            ('enable',(400,450,940,525),lambda:self.set_startup(True)),
            ('disable',(990,450,1530,525),lambda:self.set_startup(False))]:
            self.extra[key]=len(self.regions)
            self.regions.append((box,action))
        self.bind('<Escape>',lambda event:self.show_colors())
        self.canvas.bind('<Configure>',self.schedule_draw)
        self.canvas.bind('<Motion>',self.motion)
        self.canvas.bind('<Leave>',lambda e:self.set_hover(None))
        self.canvas.bind('<Button-1>',self.click)
        self.canvas.bind('<B1-Motion>',self.drag_window)
        self.canvas.bind('<ButtonRelease-1>',self.end_drag)
        self.canvas.bind('<Double-Button-1>',self.double_title)
        self.canvas.bind('<Tab>',self.next_focus)
        self.canvas.bind('<Return>',self.activate_focus)
        self.canvas.bind('<space>',self.activate_focus)
        self.status.trace_add('write',lambda *a:self.draw_status())
        self.draw()

    def on_map(self, event):
        if event.widget is self:
            self.after_idle(self.remove_native_caption)
            # Reassert the custom icon after Windows maps the borderless
            # window so the taskbar keeps the same wheel artwork.
            if hasattr(self, '_apply_window_icon'):
                self.after_idle(self._apply_window_icon)

    def remove_native_caption(self):
        # Keep a normal taskbar window: remove only the native caption/frame.
        if sys.platform != 'win32':
            return
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetParent.restype = wintypes.HWND
        user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.GetWindowLongW.restype = ctypes.c_long
        user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
        user32.SetWindowLongW.restype = ctypes.c_long
        user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                       ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        user32.SetWindowPos.restype = wintypes.BOOL
        hwnd = user32.GetParent(self.winfo_id()) or self.winfo_id()
        style = user32.GetWindowLongW(hwnd, -16)
        new_style = style & ~0x00C00000 & ~0x00040000
        if style != new_style:
            user32.SetWindowLongW(hwnd, -16, new_style)
            user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0027)
        if hasattr(self, '_apply_window_icon'):
            self._apply_window_icon()

    def in_title(self, event):
        if not hasattr(self, 'scale'):
            return False
        x = (event.x-self.ox)/self.scale
        y = (event.y-self.oy)/self.scale
        return 24 <= x < 1495 and 29 <= y <= 132

    def begin_drag(self, event):
        if self.state() == 'zoomed':
            return
        wx, wy = self.winfo_x(), self.winfo_y()
        if sys.platform == 'win32':
            u = ctypes.WinDLL('user32', use_last_error=True)
            u.GetParent.argtypes = [wintypes.HWND]
            u.GetParent.restype = wintypes.HWND
            hwnd = u.GetParent(self.winfo_id()) or self.winfo_id()
            rect = wintypes.RECT()
            u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
            if u.GetWindowRect(hwnd, ctypes.byref(rect)):
                wx, wy = rect.left, rect.top
            self.drag_hwnd = hwnd
        self.drag_origin = (event.x_root, event.y_root, wx, wy)

    def drag_window(self, event):
        if self.drag_origin and self.state() != 'zoomed':
            px, py, wx, wy = self.drag_origin
            x, y = wx + event.x_root - px, wy + event.y_root - py
            if sys.platform == 'win32':
                # Absolute desktop coordinates, including monitors left of the main one.
                u = ctypes.WinDLL('user32', use_last_error=True)
                u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
                u.SetWindowPos(self.drag_hwnd, None, x, y, 0, 0, 0x0015)
            else:
                self.geometry(f'+{x}+{y}')

    def end_drag(self, event):
        self.drag_origin = None

    def double_title(self, event):
        if self.in_title(event):
            self.drag_origin = None
            self.toggle_max()

    def toggle_max(self):
        try:self.state('normal' if self.state()=='zoomed' else 'zoomed')
        except tk.TclError:pass

    def schedule_draw(self,event=None):
        if event is not None and (event.width,event.height)==self.render_size:return
        if self.resize_job:self.after_cancel(self.resize_job)
        self.resize_job=self.after(45,self.draw)

    def coords(self,box):
        x1,y1,x2,y2=box
        return (self.ox+x1*self.scale,self.oy+y1*self.scale,
                self.ox+x2*self.scale,self.oy+y2*self.scale)

    def draw(self):
        self.resize_job=None
        w,h=self.canvas.winfo_width(),self.canvas.winfo_height()
        if w<10 or h<10:return
        self.scale=min(w/1672,h/941)
        iw,ih=round(1672*self.scale),round(941*self.scale)
        self.ox,self.oy=(w-iw)/2,(h-ih)/2
        if self.render_size != (w,h):
            self.exhaust_card_cache.clear()
            self.visual_cache.clear()
            self.photo=ImageTk.PhotoImage(self.skin.resize((iw,ih),Image.Resampling.LANCZOS))
            self.render_size = (w,h)
        self.canvas.delete('all')
        self.canvas.create_image(self.ox,self.oy,image=self.photo,anchor='nw')
        # Cover the sample path with a real editable field.
        x1,y1,x2,y2=self.coords((380,840,942,875))
        self.path_entry.configure(font=('Segoe UI',max(8,round(13*self.scale)) ))
        self.path_entry.configure(textvariable=self.exhaust_path if self.page=='exhaust' else self.game_root)
        self.path_entry.place(x=x1,y=y1,width=x2-x1,height=y2-y1)
        self.folder_entry.place_forget()
        # Correct the generated lettering using a live label in the same position.
        x1,y1,x2,y2=self.coords((108,176,286,213))
        self.canvas.create_rectangle(x1,y1,x2,y2,fill='#10132c',outline='')
        self.canvas.create_text(x1+3,(y1+y2)/2,text='CORES DO FUMO',anchor='w',fill='white',font=('Segoe UI',max(8,round(13*self.scale))))
        self.draw_language_labels()
        self.text_at(64,737,self.ui('ARRANQUE WINDOWS','WINDOWS STARTUP','INICIO WINDOWS','WINDOWS-AUTOSTART'),14,'#4ce8ff',230)
        if self.page == 'colors':
            self.draw_exhaust_tab()
        if self.page == 'language':
            self.path_entry.place_forget()
            self.draw_language_page()
        elif self.page == 'about':
            self.path_entry.place_forget()
            self.draw_about_page()
        elif self.page == 'exhaust':
            self.draw_exhaust_page()
        elif self.page in ('folders','smoke_folder','exhaust_folder','startup'):
            self.path_entry.place_forget()
            self.draw_settings_page()
        else:
            self.draw_status()
        if self.page not in ('colors',):self.draw_close_panel()
        self.draw_feedback()

    def draw_status(self):
        if not hasattr(self,'scale') or self.page != 'colors':return
        self.canvas.delete('status')
        x1,y1,x2,y2=self.coords((1260,861,1620,895))
        self.canvas.create_rectangle(x1,y1,x2,y2,fill='#03101a',outline='',tags='status')
        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text=self.tr(self.status.get()),fill='#22efda',width=x2-x1-8,
                                font=('Segoe UI',max(7,round(10*self.scale))),tags='status')

    def exhaust_label(self, key):
        return EXHAUST_LABELS.get(self.language, EXHAUST_LABELS['pt']).get(key, key.upper())

    def exhaust_text(self, key):
        return EXHAUST_UI.get(self.language, EXHAUST_UI['pt']).get(key, key)

    def exhaust_card_photo(self, key, size):
        cache_key=(key, size)
        if cache_key not in self.exhaust_card_cache:
            path=resource_path('assets/exhaust_cards') / f'{key}.png'
            image=Image.open(path).convert('RGB').resize(size, Image.Resampling.LANCZOS)
            self.exhaust_card_cache[cache_key]=ImageTk.PhotoImage(image)
        return self.exhaust_card_cache[cache_key]

    def draw_exhaust_tab(self):
        """Draw the single-window switch for the exhaust/backfire module."""
        x1,y1,x2,y2=self.coords((1170,447,1614,505))
        self.canvas.create_rectangle(x1,y1,x2,y2,fill='#11132b',outline='#c13cff',width=max(1,round(2*self.scale)),tags='exhaust_ui')
        self.canvas.create_rectangle(x1+4*self.scale,y1+4*self.scale,x2-4*self.scale,y2-4*self.scale,outline='#ff6be0',width=max(1,round(self.scale)),tags='exhaust_ui')
        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text=self.exhaust_text('tab_short'),fill='#ffffff',font=('Segoe UI',max(8,round(12*self.scale)),'bold'),tags='exhaust_ui')

    def draw_exhaust_page(self):
        """Render the exhaust colours inside the existing gamer window."""
        self.scene_panel((328,142,1632,790),0.55)
        panel=self.coords((328,190,1632,790))
        x1,y1,x2,y2=panel
        self.canvas.create_text(x1+30*self.scale,y1+28*self.scale,text=self.exhaust_text('title'),anchor='w',fill='#ffffff',font=('Segoe UI Black',max(10,round(21*self.scale))),tags='exhaust_ui')
        self.canvas.create_text(x1+30*self.scale,y1+63*self.scale,text=self.exhaust_text('sub'),anchor='w',fill='#8fb4d1',font=('Segoe UI',max(7,round(10*self.scale))),tags='exhaust_ui')
        tab=self.coords((1170,267,1614,325))
        self.canvas.create_rectangle(*tab,fill='#17102b',outline='#c13cff',width=max(1,round(2*self.scale)),tags='exhaust_ui')
        self.canvas.create_text((tab[0]+tab[2])/2,(tab[1]+tab[3])/2,text=self.exhaust_text('tab'),fill='#ffffff',font=('Segoe UI',max(8,round(12*self.scale)),'bold'),tags='exhaust_ui')
        for i,key in enumerate(EXHAUST_COLORS):
            a,b,c,d=self.coords(self.regions[self.exhaust_indices[key]][0])
            border='#ffffff' if key==self.exhaust_selected else EXHAUST_BORDER[key]
            width=max(1,round((3 if key==self.exhaust_selected else 1)*self.scale))
            photo=self.exhaust_card_photo(key,(max(20,round(296*self.scale)),max(20,round(70*self.scale))))
            self.canvas.create_image((a+c)/2,b+36*self.scale,image=photo,anchor='center',tags='exhaust_ui')
            self.canvas.create_rectangle(a,b+72*self.scale,c,d,fill='#070d19',outline='',tags='exhaust_ui')
            self.canvas.create_text((a+c)/2,b+84*self.scale,text=self.exhaust_label(key),fill='#f2fbff',font=('Segoe UI',max(7,round(12*self.scale)),'bold'),tags='exhaust_ui')
            radius=10*self.scale
            self.canvas.create_polygon(a+radius,b,c-radius,b,c,b,c,b+radius,
                c,d-radius,c,d,c-radius,d,a+radius,d,a,d,a,d-radius,a,b+radius,a,b,
                smooth=True,fill='',outline=border,width=width,tags='exhaust_ui')
        action=self.coords((1247,798,1614,854))
        self.canvas.create_rectangle(*action,fill='#15132c',outline='#18e5ff',width=max(1,round(2*self.scale)),tags='exhaust_ui')
        self.canvas.create_rectangle(action[0]+4*self.scale,action[1]+4*self.scale,action[2]-4*self.scale,action[3]-4*self.scale,outline='#c33cff',width=max(1,round(self.scale)),tags='exhaust_ui')
        self.canvas.create_text((action[0]+action[2])/2-10*self.scale,(action[1]+action[3])/2,text=self.exhaust_text('apply'),fill='#ffffff',font=('Segoe UI Black',max(8,round(12*self.scale))),tags='exhaust_ui')
        self.canvas.create_text(action[2]-20*self.scale,(action[1]+action[3])/2,text='›',fill='#8af8ff',font=('Segoe UI Black',max(12,round(19*self.scale))),tags='exhaust_ui')
        status=self.coords((1190,861,1620,895))
        self.canvas.create_rectangle(*status,fill='#03101a',outline='',tags='exhaust_ui')
        current_status=self.status.get() if hasattr(self,'status') else ''
        status_text=self.tr(current_status) if current_status.startswith('✓') else f'ESCAPE: {self.exhaust_label(self.exhaust_selected)}  •  {self.exhaust_text("ready")}'
        self.canvas.create_text((status[0]+status[2])/2,(status[1]+status[3])/2,text=status_text,fill='#22efda',font=('Segoe UI',max(7,round(9*self.scale)),'bold'),tags='exhaust_ui')
        # Keep the shared game-folder controls translated on this page too.
        self.label_cover((372,802,582,829),'PASTA DO JOGO',14)
        self.label_cover((975,842,1115,872),'PROCURAR',14)

    def draw_feedback(self):
        self.canvas.delete('feedback')
        if self.page == 'colors':
            idx=self.smoke_indices.get(self.selected)
        elif self.page == 'exhaust':
            idx=self.exhaust_indices.get(self.exhaust_selected)
        elif self.page == 'language':
            idx=self.language_index
        elif self.page=='about':
            idx=4
        else:idx=None
        for i,col,width in [(idx,'#ffffff',3),(self.hover,'#52efff',2)]:
            if i is None:continue
            self.canvas.create_rectangle(*self.coords(self.regions[i][0]),outline=col,width=width,tags='feedback')
        if idx is not None:
            x1,y1,x2,y2=self.coords(self.regions[idx][0])
            self.canvas.create_text(x2-12,y1+13,text='✓',fill='white',font=('Segoe UI',12,'bold'),tags='feedback')

    def active_indices(self):
        base=[0,1,2,3,4,self.min_index,self.max_index,self.close_index,self.language_index,self.extra['startup']]
        if self.page=='colors':
            return base+[self.exhaust_tab_index,self.browse_index,self.apply_index]+list(self.smoke_indices.values())
        if self.page=='exhaust':
            return base+[self.close_panel_index,self.exhaust_tab_index,self.browse_index,self.apply_index]+list(self.exhaust_indices.values())
        keys={'folders':['smoke_folder','exhaust_folder'],'smoke_folder':['pick_folder','save_folder'],'exhaust_folder':['pick_folder','save_folder'],'startup':['enable','disable']}.get(self.page)
        if keys is not None:return base+[self.close_panel_index]+[self.extra[k] for k in keys]
        if self.page=='language':
            return base+[self.close_panel_index]+list(range(self.language_region_start,self.language_region_start+5))
        return base+[self.close_panel_index]

    def show_about(self):
        self.change_page('about')

    def show_colors(self):
        self.change_page('colors')

    def show_exhaust(self):
        self.change_page('exhaust')

    def toggle_exhaust_page(self):
        self.change_page('colors' if self.page == 'exhaust' else 'exhaust')

    def apply_current(self):
        if self.page == 'exhaust':
            self.apply_exhaust_selected()
        else:
            self.apply_selected()

    def change_page(self, page):
        if self.page in ('smoke_folder','exhaust_folder'):
            self.save_settings()
        self.page = page
        box=(1170,267,1614,325) if page=='exhaust' else (1170,447,1614,505)
        self.regions[self.exhaust_tab_index]=(box,self.toggle_exhaust_page)
        self.hover = None
        self.focus_index = -1
        self.draw()

    def ui(self, pt, en, es, de):
        if self.language=='fr':
            french={
                'ARRANQUE WINDOWS':'DÉMARRAGE WINDOWS',
                'TAMANHO DA APP':'TAILLE DE L’APPLICATION',
                'SELECIONADO':'SÉLECTIONNÉ',
                'ESCOLHER':'CHOISIR',
                'GUARDAR E VOLTAR':'ENREGISTRER ET RETOUR',
                'ATIVAR':'ACTIVER',
                'DESATIVAR':'DÉSACTIVER',
                'ATIVADO':'ACTIVÉ',
                'DESATIVADO':'DÉSACTIVÉ',
                'PEQUENO':'PETIT',
                'MÉDIO':'MOYEN',
                'GRANDE':'GRAND',
                'AJUSTAR AO ECRÃ':'AJUSTER À L’ÉCRAN',
            }
            return french.get(pt,en)
        return {'pt':pt,'en':en,'es':es,'de':de}.get(self.language,pt)

    def save_settings(self):
        if 'exhaust_path' in self.__dict__:
            self.settings['exhaust_root']=self.exhaust_path.get().strip()
        super().save_settings()

    def choose_folder(self):
        self.change_page('exhaust_folder' if self.page=='exhaust' else 'smoke_folder')

    def scene_panel(self,box=(335,142,1634,903),shade=0.72):
        # Veil the existing single background instead of pasting a crop of
        # interface.png, which duplicated its old photograph on inner pages.
        a,b,c,d=self.coords(box)
        size=(max(1,round(c-a)),max(1,round(d-b)))
        key=(size,shade)
        if key not in self.visual_cache:
            veil=Image.new('RGBA',size,(3,10,22,max(0,min(235,round(shade*255)))))
            self.visual_cache[key]=ImageTk.PhotoImage(veil)
        self.canvas.create_image(a,b,image=self.visual_cache[key],anchor='nw')
        self.canvas.create_line(a,b,c,b,fill='#42dce8',width=1)
        self.canvas.create_line(a,d,c,d,fill='#a73bca',width=1)

    def neon_frame(self,box,color='#28dcdf'):
        a,b,c,d=self.coords(box); cut=12*self.scale
        points=(a+cut,b,c,b,c,d-cut,c-cut,d,a,d,a,b+cut)
        self.canvas.create_polygon(*points,fill='#070d18',stipple='gray75',outline=color,width=2)
        self.canvas.create_line(a+cut,b+5*self.scale,a+90*self.scale,b+5*self.scale,fill='#d4faff',width=2)
        self.canvas.create_line(c-90*self.scale,d-5*self.scale,c-cut,d-5*self.scale,fill='#cd46e8',width=2)

    def panel_button(self,key,label,size=18):
        box=self.coords(self.regions[self.extra[key]][0])
        self.neon_frame(self.regions[self.extra[key]][0])
        self.canvas.create_text((box[0]+box[2])/2,(box[1]+box[3])/2,text=label,fill='white',width=box[2]-box[0]-20,
                                font=('Segoe UI',max(8,round(size*self.scale)),'bold'))

    def draw_settings_page(self):
        self.scene_panel()
        smoke=self.ui('PASTA DO FUMO','SMOKE FOLDER','CARPETA DEL HUMO','RAUCHORDNER')
        exhaust=self.ui('PASTA DOS ESCAPES','EXHAUST FOLDER','CARPETA DEL ESCAPE','AUSPUFFORDNER')
        if self.page=='folders':
            self.text_at(375,168,self.ui('PASTAS DOS EFEITOS','EFFECT FOLDERS','CARPETAS DE EFECTOS','EFFEKTORDNER'),30,'#4ce8ff')
            self.panel_button('smoke_folder',smoke)
            self.panel_button('exhaust_folder',exhaust)
            self.text_at(400,490,self.ui('Cada efeito tem a sua pasta guardada separadamente.','Each effect has its own saved folder.','Cada efecto tiene su propia carpeta guardada.','Jeder Effekt hat einen eigenen gespeicherten Ordner.'),20)
        elif self.page in ('smoke_folder','exhaust_folder'):
            self.text_at(375,168,smoke if self.page=='smoke_folder' else exhaust,30,'#4ce8ff')
            self.text_at(395,280,self.ui('Seleciona a pasta principal do FH6 para este efeito.','Select the main FH6 folder for this effect.','Selecciona la carpeta principal de FH6 para este efecto.','Wähle den FH6-Hauptordner für diesen Effekt.'),21)
            var=self.game_root if self.page=='smoke_folder' else self.exhaust_path
            self.folder_entry.configure(textvariable=var,font=('Segoe UI',max(9,round(17*self.scale))))
            a,b,c,d=self.coords((400,390,1230,450))
            self.folder_entry.place(x=a,y=b,width=c-a,height=d-b)
            self.panel_button('pick_folder',self.tr('PROCURAR'))
            self.panel_button('save_folder',self.ui('GUARDAR E VOLTAR','SAVE AND RETURN','GUARDAR Y VOLVER','SPEICHERN UND ZURÜCK'))
        else:
            self.text_at(375,168,self.ui('ARRANQUE COM O WINDOWS','WINDOWS STARTUP','INICIO CON WINDOWS','WINDOWS-AUTOSTART'),28,'#4ce8ff')
            self.text_at(400,280,self.ui('Abre a app quando iniciares sessão no Windows. Não inicia o jogo nem aplica cores automaticamente.','Open the app when you sign in to Windows. Does not launch the game or apply colours automatically.','Abre la app al iniciar sesión en Windows. No inicia el juego ni aplica colores automáticamente.','Öffnet die App bei der Windows-Anmeldung. Startet weder das Spiel noch wendet es Farben automatisch an.'),21,width=1120)
            try: active=startup.enabled()
            except OSError: active=False
            self.text_at(400,380,self.ui('ATIVADO','ENABLED','ACTIVADO','AKTIVIERT') if active else self.ui('DESATIVADO','DISABLED','DESACTIVADO','DEAKTIVIERT'),21,'#4ce8ff')
            self.panel_button('enable',self.ui('ATIVAR','ENABLE','ACTIVAR','AKTIVIEREN'))
            self.panel_button('disable',self.ui('DESATIVAR','DISABLE','DESACTIVAR','DEAKTIVIEREN'))
            self.text_at(400,590,self.ui('Guarda a app numa pasta definitiva antes de ativar. Se a moveres, volta a ativar esta opção.','Keep the app in its permanent folder before enabling. Enable again if you move it.','Guarda la app en una carpeta definitiva antes de activar. Activa de nuevo si la mueves.','Lege die App vor dem Aktivieren dauerhaft ab. Nach dem Verschieben erneut aktivieren.'),18,width=1120)
            self.text_at(400,740,self.startup_note,18,'#ffcf70')

    def pick_module_folder(self):
        chosen=filedialog.askdirectory(parent=self,title=self.tr('Seleciona a pasta principal do Forza Horizon 6'))
        if chosen:
            (self.game_root if self.page=='smoke_folder' else self.exhaust_path).set(chosen)
            self.save_settings()

    def save_module_folder(self):
        self.save_settings()
        self.change_page('colors' if self.page=='smoke_folder' else 'exhaust')

    def set_startup(self,value):
        try:
            startup.set_enabled(value)
            self.startup_note=self.ui('Opção guardada.','Setting saved.','Opción guardada.','Einstellung gespeichert.')
        except OSError as exc:
            self.startup_note=str(exc)
        self.draw()

    def text_at(self, x, y, text, size=16, color='#e6f5ff', width=1100):
        self.canvas.create_text(self.ox+x*self.scale, self.oy+y*self.scale,
            text=self.tr(text), anchor='nw', fill=color, width=width*self.scale,
            font=('Segoe UI',max(8,round(size*self.scale))))

    def tr(self, text):
        table=getattr(self,'translations',{}).get(getattr(self,'language','pt'),{})
        if text in table:return table[text]
        # Translate dynamic status/error messages while leaving paths untouched.
        for source in sorted(table,key=len,reverse=True):
            if source not in PRESETS and source in text:text=text.replace(source,table[source])
        for name in PRESETS:
            if name in text:text=text.replace(name,table.get(name,name))
        return text

    def set_language(self, code):
        if code not in ('pt','en','es','fr','de'):return
        self.language=code
        self.settings['language']=code
        self.save_settings()
        self.hover=None
        self.draw()

    def label_cover(self, box, text, size=15, fill='#06101b'):
        x1,y1,x2,y2=self.coords(box)
        self.canvas.create_rectangle(x1,y1,x2,y2,fill=fill,outline='')
        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text=self.tr(text),fill='white',
            width=x2-x1-4,font=('Segoe UI',max(8,round(size*self.scale))))

    def draw_language_labels(self):
        # Preserve the original artwork and icons; replace only lettering where needed.
        # A plain icon and label match the original unboxed sidebar rows.
        self.canvas.create_oval(*self.coords((55,652,87,684)),outline='#25e8f4',width=2)
        self.canvas.create_oval(*self.coords((64,652,78,684)),outline='#25e8f4',width=1)
        x1,y1,x2,y2=self.coords((55,668,87,668))
        self.canvas.create_line(x1,y1,x2,y2,fill='#25e8f4',width=1)
        self.text_at(112,658,'IDIOMA',16,'#f0f5fa',184)
        if self.language=='pt':return
        labels=['CORES DO FUMO','LOCAL DO JOGO','RESTAURAR ORIGINAL','EXECUTAR FH6','SOBRE']
        for i,text in enumerate(labels):
            y=[176,264,354,445,535][i]
            self.label_cover((108,y,298,y+41),text,14,'#10132c' if i==0 else '#05101b')
        if self.page!='colors':return
        self.label_cover((359,451,950,503),'ESCOLHE A COR DO DRIFT',27)
        for i,name in enumerate(PRESETS):
            row,col=divmod(i,5);x=354+col*256;y=612+row*124
            self.label_cover((x,y,x+233,y+23),name,14)
        self.label_cover((372,802,582,829),'PASTA DO JOGO',14)
        self.label_cover((975,842,1115,872),'PROCURAR',14)
        self.label_cover((1270,808,1588,842),'APLICAR NO JOGO',19,'#10132c')

    def draw_close_panel(self):
        # Internal close returns home; the existing top-right X still closes the app.
        box=self.regions[self.close_panel_index][0]
        self.canvas.create_rectangle(*self.coords(box),fill='#0b1b2c',outline='#26dfef',width=1)
        for line in [(1580,177,1598,195),(1598,177,1580,195)]:
            self.canvas.create_line(*self.coords(line),fill='#e6faff',width=2)

    def draw_language_page(self):
        self.scene_panel()
        self.text_at(375,168,'IDIOMA',30,'#4ce8ff')
        self.text_at(375,230,'Escolhe o idioma. A escolha fica guardada automaticamente.',19)
        for i,(code,name) in enumerate([('pt','Português'),('en','English'),('es','Español'),('de','Deutsch')]):
            box=self.regions[self.language_region_start+i][0]
            self.neon_frame(box,'#4ce8ff' if code==self.language else '#9147b4')
            key=('flag',code,round(96*self.scale))
            if key not in self.visual_cache:
                flag=Image.open(resource_path('assets/flags')/f'{code}.png').convert('RGBA')
                flag.thumbnail((max(1,round(96*self.scale)),max(1,round(64*self.scale))),Image.Resampling.LANCZOS)
                self.visual_cache[key]=ImageTk.PhotoImage(flag)
            self.canvas.create_image(self.ox+465*self.scale,self.oy+(box[1]+55)*self.scale,image=self.visual_cache[key])
            self.text_at(550,box[1]+34,name+('  ✓' if code==self.language else ''),26)

    def draw_about_page(self):
        self.scene_panel()
        self.text_at(375,168,'SOBRE A APLICAÇÃO',30,'#4ce8ff')
        self.text_at(375,224,'FH6 RGB SMOKE CONTROLLER  •  5.2.0  •  RICARDOSTONEPT',17,'#ca91ff')
        sections=[
            ('01  ESCOLHER A COR','Em CORES DO FUMO, seleciona um cartão. A seleção fica assinalada. As cores são aplicadas ao efeito de partículas do pneu. O cartão RGB continua experimental neste modo.'),
            ('02  LOCALIZAR E APLICAR','Fecha o jogo, escolhe a pasta principal do FH6 e usa APLICAR NO JOGO na área do fumo ou APLICAR ESCAPE na área do escape. A app usa os efeitos XML do fumo e os packs .swatchbin do escape.'),
            ('03  BACKUP E RESTAURO','Antes da primeira substituição é guardada uma cópia do ficheiro. RESTAURAR ORIGINAL permite recuperar essa cópia.'),
            ('04  COMPATIBILIDADE','O FH6 deve estar fechado durante a instalação. Depois reinicia o jogo. O fumo usa o rasto diurno reforçado e o escape mantém backup automático por instalação. RESTAURAR ORIGINAL recupera ambos.')]
        sections=[
            (self.ui('01  COR DO DRIFT','01  DRIFT COLOUR','01  COLOR DEL DERRAPE','01  DRIFTFARBE'),
             self.ui('Escolhe uma cor em CORES DO FUMO e usa APLICAR NO JOGO. O efeito dos pneus passa a poeira colorida com rasto reforçado para dia e noite. Pode deixar rasto fora do drift. RGB ainda não é suportado neste modo.',
             'Choose a smoke colour and click APPLY TO GAME. Tire smoke is replaced with coloured dust and a stronger day/night trail. A trail may remain outside a drift. RGB is not yet supported in this mode.',
             'Elige un color del humo y pulsa APLICAR AL JUEGO. Se usa polvo coloreado con un rastro reforzado de día y noche. Puede dejar rastro fuera del derrape. RGB aún no es compatible.',
             'Wähle eine Rauchfarbe und klicke auf IM SPIEL ANWENDEN. Farbiger Staub mit verstärkter Spur ersetzt den Reifenrauch bei Tag und Nacht. Spuren sind auch ohne Drift möglich. RGB wird noch nicht unterstützt.')),
            (self.ui('02  CORES DO ESCAPE','02  EXHAUST COLOURS','02  COLORES DEL ESCAPE','02  AUSPUFFFARBEN'),
             self.ui('Escolhe um dos 16 cartões e usa APLICAR ESCAPE. A app instala o pack de cor das chamas, incluindo combinações duplas. O efeito aparece quando o carro produz backfire; não força chamas contínuas nem altera o som.',
             'Choose one of the 16 cards and click APPLY EXHAUST. The app installs a flame colour pack, including dual combinations. It appears when the car produces backfire; it does not force continuous flames or change sound.',
             'Elige una de las 16 tarjetas y pulsa APLICAR ESCAPE. Se instala un paquete de color, incluidas combinaciones dobles. Aparece cuando el coche produce backfire; no fuerza llamas continuas ni cambia el sonido.',
             'Wähle eine der 16 Karten und AUSPUFF ANWENDEN. Die App installiert Flammenfarben, auch Zweifarbkombinationen. Sichtbar bei Fehlzündungen; keine erzwungenen Dauerflammen und keine Tonänderung.')),
            (self.ui('03  PASTAS E APLICAÇÃO','03  FOLDERS AND APPLYING','03  CARPETAS Y APLICACIÓN','03  ORDNER UND ANWENDEN'),
             self.ui('Fecha o FH6 antes de aplicar. Em LOCAL DO JOGO, guarda a pasta do fumo e a pasta dos escapes separadamente. Podem apontar para a mesma instalação. Aplica cada efeito e volta a abrir o jogo.',
             'Close FH6 before applying. In GAME FOLDER, save the smoke and exhaust folders separately. Both may point to the same installation. Apply each effect and reopen the game.',
             'Cierra FH6 antes de aplicar. Guarda las carpetas de humo y escape por separado. Pueden apuntar a la misma instalación. Aplica cada efecto y abre de nuevo el juego.',
             'Schließe FH6 vor dem Anwenden. Speichere Rauch- und Auspuffordner getrennt. Beide dürfen auf dieselbe Installation zeigen. Wende jeden Effekt an und öffne das Spiel erneut.')),
            (self.ui('04  BACKUP E RESTAURO','04  BACKUP AND RESTORE','04  COPIA Y RESTAURACIÓN','04  SICHERUNG UND WIEDERHERSTELLUNG'),
             self.ui('A app guarda os ficheiros existentes antes de os substituir. RESTAURAR ORIGINAL recupera ambos os efeitos; os ficheiros criados pela app são removidos quando não existia um original solto. Fecha o jogo antes de restaurar.',
             'Existing files are backed up before replacement. RESTORE ORIGINAL restores both effects; files created by the app are removed when no loose original existed. Close the game before restoring.',
             'Los archivos existentes se guardan antes de sustituirlos. RESTAURAR ORIGINAL recupera ambos efectos; elimina los archivos creados si no existía un original suelto. Cierra el juego antes de restaurar.',
             'Vorhandene Dateien werden vor dem Ersetzen gesichert. ORIGINAL WIEDERHERSTELLEN setzt beide Effekte zurück; neu angelegte Dateien ohne loses Original werden entfernt. Schließe das Spiel vorher.'))]
        for i,(title,body) in enumerate(sections):
            y=285+i*137
            self.neon_frame((373,y,1593,y+118))
            self.text_at(396,y+14,title,19,'#4ce8ff')
            self.text_at(396,y+49,body,17,width=1165)
        self.text_at(396,855,'Volta às cores através do menu lateral. Arrasta a app pelo cabeçalho.',15,'#9ab9d4')

    def hit(self,e):
        if not hasattr(self,'scale'):return None
        x,y=(e.x-self.ox)/self.scale,(e.y-self.oy)/self.scale
        return next((i for i,(b,f) in enumerate(self.regions) if i in self.active_indices() and b[0]<=x<=b[2] and b[1]<=y<=b[3]),None)

    def set_hover(self,i):
        if self.hover!=i:self.hover=i;self.draw_feedback()
        self.canvas.configure(cursor='hand2' if i is not None else '')

    def motion(self,e):self.set_hover(self.hit(e))
    def click(self,e):
        self.canvas.focus_set()
        self.drag_origin = None
        if self.in_title(e):self.begin_drag(e)
        i=self.hit(e)
        if i is not None:self.regions[i][1]()
    def next_focus(self,e):
        active=self.active_indices()
        self.focus_index=active[(active.index(self.focus_index)+1)%len(active)] if self.focus_index in active else active[0]
        self.set_hover(self.focus_index)
        return 'break'
    def activate_focus(self,e):
        if self.focus_index in self.active_indices():self.regions[self.focus_index][1]()
        return 'break'

    def select_exhaust(self, name):
        if name not in EXHAUST_COLORS:
            return
        self.exhaust_selected=name
        self.settings['exhaust_color']=name
        self.save_settings()
        self.status.set('ESCAPE SELECIONADO: '+self.exhaust_label(name))
        self.draw()

    def apply_exhaust_selected(self):
        self.save_settings()
        try:
            installed=self.apply_exhaust_color(self.exhaust_selected)
            label=self.exhaust_label(self.exhaust_selected)
            self.status.set('✓ ESCAPE '+label+' INSTALADO — REINICIA O JOGO')
            messagebox.showinfo(APP_NAME, (
                f'Cor do escape {label} instalada com sucesso.\n\n'
                f'Ficheiros .swatchbin aplicados: {len(installed)}\n\n'
                'Fecha e volta a abrir o FH6 para carregar as chamas.'
            ))
        except PermissionError:
            messagebox.showerror(APP_NAME, 'O Windows bloqueou a escrita. Fecha o jogo e executa esta app como administrador.')
        except Exception as exc:
            messagebox.showerror(APP_NAME, f'Não foi possível aplicar o escape:\n{exc}')
        self.draw()

    def select(self,name):
        self.selected=name
        self.status.set('SELECIONADO: '+name)
        self.draw_feedback()

if __name__=='__main__':
    try:ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:pass
    GamerApp().mainloop()
