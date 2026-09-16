"""FH6 5.11.1: one continuous GTR background, clean navigation and soft lamp pulse."""
import ctypes
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageDraw
from legacy_ui import GamerApp as WindowBase, EXHAUST_BORDER
from controller import APP_NAME, APP_VERSION, PRESETS, EXHAUST_COLORS, RGB_SELECTION, resource_path
from visuals import neon_button, card_surface, selection_glow, flag_plaque, rgb_glow, rgb_text, rgb_halo, red_lights_glow, clean_active_frame
from pages import Pages
import startup

SIZES={'small':(1100,619),'medium':(1400,788),'large':(1672,941)}

class GamerApp(Pages,WindowBase):
    def __init__(self):
        if sys.platform=='win32':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('RicardoStonePT.FH6RGB.Controller')
        super().__init__()
        self.title(f'{APP_NAME} — {APP_VERSION}')
        self.attributes('-alpha',1.0)
        self.minsize(900,507)
        self.items={};self.image_cache={};self.frame_refs=[];self.text_boxes=[];self.smoke_card_cache={}
        self.body_image=ImageOps.fit(self._bg_src,(1672,941),Image.Resampling.LANCZOS)
        # Keep one photograph across the complete canvas. The previous
        # composition started from interface.png (which already contained a
        # different photograph) and pasted the GTR over its middle.
        self.clean_skin=ImageEnhance.Brightness(self.body_image).enhance(0.78)
        self.logo_source=Image.open(resource_path('assets/logo_clean.png')).convert('RGBA')
        # Precompute a few low-intensity frames. Cycling the alpha of the
        # existing bloom gives the GT-R's rear lights a soft pulse without
        # repeatedly running large blur filters on the Tk main thread.
        light_base=red_lights_glow((1672,941))
        self.taillight_frames=[]
        for strength in (0.74,0.80,0.89,0.98,1.04,0.98,0.89,0.80):
            frame=light_base.copy()
            alpha=light_base.getchannel('A').point(lambda value,s=strength:max(0,min(255,round(value*s))))
            frame.putalpha(alpha)
            self.taillight_frames.append(frame)
        self.light_frame_index=0
        self.taillight_glow=self.taillight_frames[0]
        self.page='colors'
        self.size_choice=self.settings.get('window_size','medium')
        self.selected=self.settings.get('smoke_color','CIANO')
        if self.selected not in PRESETS:self.selected='CIANO'
        # The repository ships an optimised 512 px copy for the interface.
        # The multi-size ICO remains the authoritative Windows/taskbar icon.
        self.icon_source=Image.open(resource_path('assets/app_icon_ui.png')).convert('RGBA')
        self.reference_icons=self.load_reference_icons()
        self.icon_refs=[ImageTk.PhotoImage(self.icon_source.resize((s,s),Image.Resampling.LANCZOS)) for s in (16,32,48,64,256)]
        self._apply_window_icon()
        raw=self.exhaust_path.get().strip()
        if raw and Path(raw).name.casefold()!='mediapc':self.exhaust_path.set(str(self.exhaust_media_root()))
        self.after(140,self.animate_taillights)
        self.after(80,lambda:self.resize_choice(self.size_choice,save=False))

    def animate_taillights(self):
        """Give the rear lamps a restrained, slow breathing effect."""
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        self.light_frame_index=(self.light_frame_index+1)%len(self.taillight_frames)
        self.taillight_glow=self.taillight_frames[self.light_frame_index]
        # Update only the existing glow layer. Redrawing the complete canvas
        # every 140 ms also redrew the path entry and hover state, which made
        # the lower bar appear to blink while the pointer was over a colour.
        item=getattr(self,'taillight_item',None)
        try:
            if item:
                size=(max(1,round(1672*self.scale)),max(1,round(941*self.scale)))
                key=(('taillight-glow',self.light_frame_index),size)
                photo=self.image_cache.get(key)
                if photo is None:
                    photo=ImageTk.PhotoImage(self.taillight_glow.resize(size,Image.Resampling.LANCZOS))
                    self.image_cache[key]=photo
                self.canvas.itemconfigure(item,image=photo)
            else:
                self.queue_draw()
        except (AttributeError,tk.TclError):
            self.queue_draw()
        self.after(140,self.animate_taillights)

    def _apply_window_icon(self):
        """Keep the custom wheel icon on the window and Windows taskbar."""
        try:
            self.iconbitmap(str(resource_path('assets/app_icon.ico')))
        except tk.TclError:
            pass
        try:
            self.iconphoto(True,*self.icon_refs)
        except (AttributeError,tk.TclError):
            pass

    def build_ui(self):
        self.bg_label.destroy()
        self.canvas=tk.Canvas(self,bg='#040710',highlightthickness=0)
        self.canvas.pack(fill='both',expand=True)
        self.path_entry=tk.Entry(self.canvas,bg='#07111f',fg='#d5ecff',insertbackground='white',relief='flat',bd=0)
        self.folder_entry=tk.Entry(self.canvas,bg='#07111f',fg='#d5ecff',insertbackground='white',relief='flat',bd=0)
        for entry in (self.path_entry,self.folder_entry):entry.bind('<FocusOut>',lambda event:self.save_settings())
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
        self.bind('<Escape>',lambda e:self.show_colors())
        self.status.trace_add('write',lambda *a:self.queue_draw())
        self.draw()

    def queue_draw(self):
        if 'canvas' in self.__dict__ and not self.resize_job:self.resize_job=self.after_idle(self.draw)

    def text_box(self,box,text,size=18,color='#e6f5ff',bold=False,align='left',tag='text',italic=False,valign='top',single_line=False):
        text=str(text);x,y,r,b=self.coords(box);pixels=max(8,round(size*self.scale))
        weight='bold' if bold else 'normal';slant='italic' if italic else 'roman'
        ident=self.canvas.create_text(x,y,anchor='nw',text=text,fill=color,width=0 if single_line else max(1,r-x),justify=align,
            font=('Segoe UI',-pixels,weight,slant),tags=(tag,))
        while pixels>8:
            bounds=self.canvas.bbox(ident)
            if bounds and bounds[3]-bounds[1]<=b-y and bounds[2]-bounds[0]<=r-x+4:break
            pixels-=1;self.canvas.itemconfigure(ident,font=('Segoe UI',-pixels,weight,slant))
        bounds=self.canvas.bbox(ident)
        if single_line and bounds and bounds[2]-bounds[0]>r-x+4:
            self.canvas.itemconfigure(ident,width=max(1,r-x))
        if align=='center' or valign=='center':
            bounds=self.canvas.bbox(ident)
            if bounds:self.canvas.move(ident,((r-x)-(bounds[2]-bounds[0]))/2 if align=='center' else 0,((b-y)-(bounds[3]-bounds[1]))/2)
        self.text_boxes.append((ident,(x,y,r,b),text));return ident

    def picture(self,key,source,box,tags=None):
        a,b,c,d=self.coords(box);size=(max(1,round(c-a)),max(1,round(d-b)));key=(key,size)
        if key not in self.image_cache:self.image_cache[key]=ImageTk.PhotoImage(source.resize(size,Image.Resampling.LANCZOS))
        photo=self.image_cache[key];self.frame_refs.append(photo)
        options={'image':photo,'anchor':'nw'}
        if tags:options['tags']=tags
        return self.canvas.create_image(a,b,**options)

    def glow(self,box,selected=False):
        a,b,c,d=self.coords(box);size=(max(1,round(c-a)),max(1,round(d-b)));key=('neon',size,selected)
        if key not in self.image_cache:self.image_cache[key]=ImageTk.PhotoImage(neon_button(size,selected))
        self.frame_refs.append(self.image_cache[key]);self.canvas.create_image(a-12,b-12,image=self.image_cache[key],anchor='nw')

    def rgb_frame(self,box,selected=False):
        """Add a subtle RGB edge without covering the artwork underneath."""
        a,b,c,d=self.coords(box);size=(max(1,round(c-a)),max(1,round(d-b)))
        key=('rgb-frame',size,selected)
        if key not in self.image_cache:
            self.image_cache[key]=ImageTk.PhotoImage(rgb_glow(size,selected))
        self.frame_refs.append(self.image_cache[key]);self.canvas.create_image(a,b,image=self.image_cache[key],anchor='nw')

    def clean_active_frame(self,box):
        a,b,c,d=self.coords(box);size=(max(1,round(c-a)),max(1,round(d-b)))
        key=('clean-active-frame',size)
        if key not in self.image_cache:
            self.image_cache[key]=ImageTk.PhotoImage(clean_active_frame(size))
        self.frame_refs.append(self.image_cache[key]);self.canvas.create_image(a,b,image=self.image_cache[key],anchor='nw')

    def button(self,key,box,label,action,icon=None,selected=False,size=17):
        self.items[key]=(box,action);self.glow(box,selected or self.hover==key);x,y,r,b=box
        if icon:self.symbol(icon,x+22,(y+b)/2-17,34)
        self.text_box((x+(68 if icon else 15),y+9,r-15,b-9),label,size,bold=True,align='left' if icon else 'center',valign='center',single_line='\n' not in label)

    def symbol(self,name,x,y,size=32):
        def line(points):
            pts=[]
            for a,b in points:pts.extend((self.ox+(x+a*size)*self.scale,self.oy+(y+b*size)*self.scale))
            self.canvas.create_line(*pts,fill='#44e9f6',width=max(1,2*self.scale))
        def oval(box):
            self.canvas.create_oval(*self.coords((x+box[0]*size,y+box[1]*size,x+box[2]*size,y+box[3]*size)),outline='#44e9f6',width=max(1,2*self.scale))
        if name=='folder':
            line([(0,.2),(.35,.2),(.48,.34),(1,.34),(1,.92),(0,.92),(0,.2)]);line([(0,.46),(1,.46)])
        elif name=='windows':
            for ax,ay in ((0,0),(.57,0),(0,.57),(.57,.57)):line([(ax,ay),(ax+.4,ay),(ax+.4,ay+.4),(ax,ay+.4),(ax,ay)])
        elif name=='size':
            for pts in [[(0,.32),(0,0),(.32,0)],[(.68,0),(1,0),(1,.32)],[(0,.68),(0,1),(.32,1)],[(.68,1),(1,1),(1,.68)]]:line(pts)
        elif name=='globe':oval((0,0,1,1));oval((.26,0,.74,1));line([(0,.5),(1,.5)])
        elif name=='restore':oval((.06,.06,.94,.94));line([(0,.02),(0,.35),(.34,.35)])
        elif name=='palette':
            # Palette icon from the reference: round palette with four colour
            # wells and a thumb cut-out, not a plain circle.
            oval((0.04,0.08,.94,.94))
            for cx,cy in ((.31,.28),(.56,.22),(.76,.42),(.60,.68)):
                oval((cx-.06,cy-.06,cx+.06,cy+.06))
            self.canvas.create_oval(*self.coords((x+.10*size,y+.62*size,x+.32*size,y+.84*size)),fill='#040a15',outline='')
        elif name=='fire':
            line([(0.50,1.0),(0.22,.84),(.16,.58),(.31,.67),(.28,.36),(.50,.08),(.58,.34),(.76,.17),(.84,.50),(.77,.77),(.50,1.0)])
            for a,b in ((.28,.24),(.55,.2),(.73,.4),(.33,.58)):oval((a,b,a+.11,b+.11))
        elif name=='play':oval((0,0,1,1));line([(.4,.28),(.74,.5),(.4,.73),(.4,.28)])
        else:oval((0,0,1,1));line([(.5,.43),(.5,.77)]);oval((.47,.23,.53,.29))

    def load_reference_icons(self):
        """Extract the cyan glyphs from the supplied sidebar reference.

        Keeping these as tiny transparent assets makes the sidebar use the
        exact palette/flame/folder/play/info/globe/Windows/monitor shapes the
        user selected, instead of an approximate font or line icon.
        """
        icon_dir=resource_path('assets/sidebar_icons')
        if icon_dir.exists():
            files={p.stem:p for p in icon_dir.glob('*.png')}
            if all(k in files for k in ('palette','fire','folder','restore','play','info','globe','windows','size')):
                return {k:Image.open(files[k]).convert('RGBA') for k in files}
        path=resource_path('assets/reference_sidebar.png')
        if not path.exists():return {}
        source=Image.open(path).convert('RGBA')
        crops={'palette':(45,202,101,251),'fire':(48,276,101,326),
          'folder':(45,345,104,393),'restore':(45,415,101,466),
          'play':(48,485,101,537),'info':(45,577,101,628),
          'globe':(45,643,102,695),'windows':(45,711,101,759),
          'size':(45,777,105,826)}
        result={}
        for name,box in crops.items():
            crop=source.crop(box)
            px=crop.load()
            for yy in range(crop.height):
                for xx in range(crop.width):
                    r,g,b,a=px[xx,yy]
                    # Preserve cyan strokes/glow, discard the dark panel.
                    strength=(max(0,min(255,int((g+b-2*r)*1.5)))
                              if b>80 and g>70 and b>r+35 else 0)
                    px[xx,yy]=(0,225,255,strength)
            result[name]=crop
        return result

    def reference_icon(self,name,box):
        image=self.reference_icons.get(name)
        if image is not None:self.picture(('ref-icon',name),image,box)
        else:
            x,y,r,b=box;self.symbol(name,x,y,r-x)

    def draw(self):
        self.resize_job=None;w,h=self.canvas.winfo_width(),self.canvas.winfo_height()
        if min(w,h)<10:return
        self.scale=min(w/1672,h/941);self.ox=(w-1672*self.scale)/2;self.oy=(h-941*self.scale)/2
        if self.render_size!=(w,h):self.image_cache.clear()
        self.render_size=(w,h);self.canvas.delete('all');self.items={};self.text_boxes=[];self.frame_refs=[]
        self.taillight_item=None
        self.path_entry.place_forget();self.folder_entry.place_forget()
        # All pages use the same single GTR scene. Other layouts are
        # translucent overlays, never a second photograph pasted over it.
        self.picture('skin',self.clean_skin,(0,0,1672,941))
        light_index=getattr(self,'light_frame_index',0)
        light_image=(self.taillight_frames[light_index]
                     if hasattr(self,'taillight_frames') else self.taillight_glow)
        self.taillight_item=self.picture(('taillight-glow',light_index),light_image,(0,0,1672,941),tags=('taillight-layer',))
        header=Image.new('RGBA',(1628,106),(3,9,19,88))
        self.picture('header-glass',header,(22,28,1650,134))
        self.canvas.create_rectangle(*self.coords((22,28,1650,914)),outline='#29485e',width=max(1,round(self.scale)))
        # Transparent wordmark: the selected GTR artwork remains visible
        # around it instead of bringing the old interface photo along.
        self.picture('brand-logo',self.logo_source,(40,40,465,114))
        if self.page!='colors':
            glass=Image.new('RGBA',(1324,780),(3,10,22,72))
            self.picture('page-glass',glass,(326,134,1650,914))
        self.draw_sidebar();self.picture('brand-icon',self.icon_source,(1410,39,1466,95))
        # Minimal window controls stay visible after removing the baked UI
        # template: line, square and X in the same restrained style.
        self.canvas.create_line(*self.coords((1512,56,1530,56)),fill='#dcefff',width=max(1,round(1.5*self.scale)))
        self.canvas.create_rectangle(*self.coords((1558,47,1576,65)),outline='#dcefff',width=max(1,round(1.2*self.scale)))
        self.canvas.create_line(*self.coords((1608,47,1628,66)),fill='#dcefff',width=max(1,round(1.5*self.scale)))
        self.canvas.create_line(*self.coords((1628,47,1608,66)),fill='#dcefff',width=max(1,round(1.5*self.scale)))
        for key,box,action in [('min',(1500,38,1540,73),self.iconify),('max',(1548,38,1588,73),self.toggle_max),('quit',(1599,38,1640,73),self.destroy)]:self.items[key]=(box,action)
        if self.page in ('colors','exhaust'):self.draw_colors()
        elif self.page=='folders':self.draw_folders()
        elif self.page in ('smoke_folder','exhaust_folder'):self.draw_folder()
        elif self.page=='language':self.draw_languages()
        elif self.page=='about':self.draw_about()
        elif self.page=='sizes':self.draw_sizes()
        elif self.page=='startup':self.draw_startup()
        if self.page!='colors':self.button('back',(1565,154,1617,202),'×',self.show_colors,size=25)
        self.draw_feedback()

    def draw_sidebar(self):
        # Single-column glass navigation matching the reference sidebar.
        self.canvas.create_rectangle(*self.coords((23,134,324,913)),fill='#040a15',outline='#18334b')
        data=[('colors',self.tr('CORES DO FUMO'),'palette',self.show_colors),
          ('exhaust',self.exhaust_text('tab_short'),'fire',lambda:self.change_page('exhaust')),
          ('folders',self.tr('LOCAL DO JOGO'),'folder',lambda:self.change_page('folders')),
          ('restore',self.tr('RESTAURAR ORIGINAL'),'restore',self.restore_original),
          ('launch',self.tr('EXECUTAR FH6'),'play',self.launch_game),
          ('about',self.tr('SOBRE'),'info',self.show_about),
          ('language',self.tr('IDIOMA'),'globe',lambda:self.change_page('language')),
          ('startup',self.ui('ARRANQUE WINDOWS','WINDOWS STARTUP','INICIO WINDOWS','WINDOWS-AUTOSTART'),'windows',lambda:self.change_page('startup')),
          ('sizes',self.ui('TAMANHO DA APP','APP SIZE','TAMAÑO DE LA APP','APP-GRÖSSE'),'size',lambda:self.change_page('sizes'))]
        active='folders' if self.page in ('folders','smoke_folder','exhaust_folder') else self.page
        for i,(key,label,icon,action) in enumerate(data):
            if i==5:self.canvas.create_line(*self.coords((49,535,298,535)),fill='#2bcce0',width=max(1,1*self.scale))
            y=150+i*76;box=(36,y,305,y+58);self.items['nav_'+key]=(box,action)
            if active==key:
                # One RGB edge only. The old neon_button contained a second
                # rounded inner panel, which made the active row look doubled.
                self.canvas.create_rectangle(*self.coords(box),fill='#061323',outline='')
                self.clean_active_frame(box)
            elif self.hover=='nav_'+key:
                # Hover is deliberately a quiet fill, not a second neon
                # frame. This keeps the active CORES DO FUMO row from looking
                # duplicated when the pointer passes over another item.
                self.canvas.create_rectangle(*self.coords(box),fill='#0a1d31',outline='#2a7897',width=max(1,1*self.scale))
            else:
                self.canvas.create_rectangle(*self.coords(box),fill='#061323',outline='#1a4560',width=max(1,1*self.scale))
            self.reference_icon(icon,(48,y+10,86,y+48))
            # Keep the navigation column clean and readable. Only the
            # ESCAPE / BACKFIRE entry carries the RGB title treatment.
            if key=='exhaust':
                self.rgb_title((91,y+7,268,y+51),label,15)
            else:
                self.text_box((91,y+7,268,y+51),label,15,'#e6f5ff',bold=True,
                              valign='center',single_line=True)
            self.text_box((276,y+14,296,y+43),'›',24,'#dcefff',align='center',valign='center',single_line=True)
        self.text_box((48,875,298,901),f'RICARDOSTONEPT  /  {APP_VERSION}',12,'#7895b0')

    def headline(self,title,subtitle=''):
        self.rgb_title((369,166,1530,217),title,30)
        if subtitle:self.text_box((370,226,1515,277),subtitle,18,'#b0c9df')

    def rgb_title(self,box,title,size=30):
        """Draw RGB colour inside the title letters (no underline)."""
        a,b,c,d=self.coords(box)
        dims=(max(1,round(c-a)),max(1,round(d-b)))
        key=('rgb-title',dims,str(title),int(size))
        if key not in self.image_cache:
            self.image_cache[key]=ImageTk.PhotoImage(rgb_text(dims,str(title),int(size),glow=True))
        self.frame_refs.append(self.image_cache[key])
        self.canvas.create_image(a,b,image=self.image_cache[key],anchor='nw')

    def rgb_logo_halo(self,box):
        """Add colour glow around the existing logo without replacing it."""
        a,b,c,d=self.coords(box)
        dims=(max(1,round(c-a)),max(1,round(d-b)))
        key=('rgb-logo-halo',dims)
        if key not in self.image_cache:
            self.image_cache[key]=ImageTk.PhotoImage(rgb_halo(dims,'FH6 RGB SMOKE',36))
        self.frame_refs.append(self.image_cache[key])
        self.canvas.create_image(a,b,image=self.image_cache[key],anchor='nw')

    def draw_colors(self):
        smoke=self.page=='colors'
        if smoke:
            self.rgb_title((350,445,1050,520),self.tr('ESCOLHE A COR DO DRIFT'),34)
            entries=list(PRESETS)
        else:
            self.headline(self.ui('ESCOLHE A COR DO ESCAPE','CHOOSE YOUR EXHAUST COLOUR','ELIGE EL COLOR DEL ESCAPE','WÄHLE DEINE AUSPUFFFARBE'),self.ui('18 cores • Cores simples e duplas','18 colours • Single and dual colours','18 colores • Simples y dobles','18 Farben • Einzel- und Zweifarbkombinationen'))
            entries=list(EXHAUST_COLORS)
        for i,key in enumerate(entries):
            if smoke:
                row,col=divmod(i,5);x=351+col*256;y=520+row*88;w=240;h=78
                # Use dedicated smoke thumbnails. They are generated from
                # the original card artwork at build time, so the runtime
                # never loads the old composite screenshot and every colour
                # remains visible in the Python build.
                slug={'ORIGINAL':'original', 'AZUL NEON':'azul_neon',
                      'ROXO ELÉTRICO':'roxo_eletrico', 'ROSA NEON':'rosa_neon',
                      'VERMELHO':'vermelho', 'LARANJA':'laranja',
                      'VERDE ÁCIDO':'verde_acido', 'CIANO':'ciano',
                      'DOURADO':'dourado', 'TURQUESA NEON':'turquesa_neon',
                      'MAGENTA NEON':'magenta_neon', 'LIMA NEON':'lima_neon',
                      'AMARELO NEON':'amarelo_neon',
                      'ULTRAVIOLETA NEON':'ultravioleta_neon',
                      'RGB':'rgb'}.get(key)
                if not slug:
                    raise FileNotFoundError(f'Preview de fumo inválido: {key}')
                preset_path=resource_path('assets/smoke_cards') / f'{slug}.png'
                if key not in self.smoke_card_cache:
                    self.smoke_card_cache[key]=Image.open(preset_path).convert('RGB')
                source=self.smoke_card_cache[key]
                value=PRESETS[key];color='#a3acb5' if value is None else ('#ba4cff' if value=='rgb' else '#%02x%02x%02x'%value)
                label=self.tr(key);action=lambda k=key:self.select(k);selected=self.selected==key
            else:
                row,col=divmod(i,6);x=351+col*212;y=407+row*120;w=198;h=108
                source=Image.open(resource_path('assets/exhaust_cards')/f'{key}.png')
                color=EXHAUST_BORDER[key];label=self.exhaust_label(key);action=lambda k=key:self.select_exhaust(k);selected=self.exhaust_selected==key
            if selected:
                self.picture(('selected-glow',smoke,key),selection_glow((w,h),color),(x-9,y-9,x+w+9,y+h+9))
            self.picture(('card',smoke,key),card_surface(source,(w,h),color),(x,y,x+w,y+h))
            self.items['card_'+key]=((x,y,x+w,y+h),action)
            self.text_box((x+7,y+h-25,x+w-7,y+h-3),label,13,align='center')
        self.draw_pathbar(smoke)

    def draw_pathbar(self,smoke):
        self.canvas.create_rectangle(*self.coords((345,789,1632,903)),fill='#050b16',outline='#285166')
        caption=self.ui('PASTA DO FUMO  ·  FORZA HORIZON 6','SMOKE FOLDER  ·  FORZA HORIZON 6','CARPETA DEL HUMO  ·  FORZA HORIZON 6','RAUCHORDNER  ·  FORZA HORIZON 6') if smoke else self.ui('PASTA DOS ESCAPES  ·  MEDIAPC','EXHAUST FOLDER  ·  MEDIAPC','CARPETA DEL ESCAPE  ·  MEDIAPC','AUSPUFFORDNER  ·  MEDIAPC')
        self.text_box((371,802,1124,827),caption,14,'#a5c3d9')
        self.entry_at(self.path_entry,self.game_root if smoke else self.exhaust_path,(378,841,940,875),15)
        self.button('browse',(963,835,1137,886),self.tr('PROCURAR'),self.choose_folder,size=15)
        self.button('apply',(1247,798,1614,854),self.tr('APLICAR NO JOGO') if smoke else self.exhaust_text('apply'),self.apply_current,size=19)
        self.text_box((1180,866,1618,897),self.tr(self.status.get()),12,'#30e5cb',align='center')

    def entry_at(self,entry,var,box,size):
        a,b,c,d=self.coords(box);entry.configure(textvariable=var,font=('Segoe UI',-max(9,round(size*self.scale))))
        entry.place(x=a,y=b,width=c-a,height=d-b)

    def resize_choice(self,key,save=True):
        if key not in (*SIZES,'screen'):key='medium'
        maxw,maxh=self.winfo_screenwidth()-40,self.winfo_screenheight()-90
        if sys.platform=='win32':
            from ctypes import wintypes
            rect=wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(48,0,ctypes.byref(rect),0):maxw,maxh=rect.right-rect.left-24,rect.bottom-rect.top-24
        requested=SIZES.get(key,(maxw,maxh));width=min(requested[0],maxw,round(maxh*1672/941));height=round(width*941/1672)
        self.state('normal');self.minsize(min(900,width),min(507,height));self.geometry(f'{width}x{height}');self.size_choice=key
        if save:self.settings['window_size']=key;self.save_settings()
        self.queue_draw()

    def change_page(self,page):
        if page not in ('colors','exhaust','folders','smoke_folder','exhaust_folder','about','language','startup','sizes'):return
        if self.page in ('smoke_folder','exhaust_folder'):self.save_settings()
        self.page=page;self.hover=None;self.focus_index=None;self.draw()

    def select(self,name):
        self.selected=name;self.settings['smoke_color']=name;self.save_settings()
        self.status.set(self.tr(RGB_SELECTION) if name=='RGB' else self.tr('SELECIONADO: ')+self.tr(name));self.draw()

    def pick_module_folder(self):
        smoke=self.page=='smoke_folder';chosen=filedialog.askdirectory(parent=self,title=self.folder_caption(smoke))
        if chosen:(self.game_root if smoke else self.exhaust_path).set(chosen);self.save_settings();self.draw()

    def save_module_folder(self):
        smoke=self.page=='smoke_folder';raw=(self.game_root if smoke else self.exhaust_path).get().strip().strip('"')
        if not raw or not Path(raw).is_dir():messagebox.showerror(APP_NAME,self.folder_caption(smoke),parent=self);return
        if smoke and Path(raw).name.casefold() in ('mediapc','media','content'):self.game_root.set(str(self.resolved_game_root()))
        elif not smoke and Path(raw).name.casefold()!='mediapc':self.save_settings();self.exhaust_path.set(str(self.exhaust_media_root()))
        self.save_settings();self.change_page('colors' if smoke else 'exhaust')

    def draw_feedback(self):
        # This is the v5.10 hover treatment: one cyan neon halo follows the
        # pointer. Animation now updates only the taillight layer, so this
        # glow stays stable instead of making the path bar blink.
        self.canvas.delete('feedback');self.canvas.delete('hover-glow');key=self.hover
        if key not in self.items:return
        x1,y1,x2,y2=self.items[key][0]
        w=max(1,round((x2-x1)*self.scale));h=max(1,round((y2-y1)*self.scale))
        self.picture(('hover-glow',key),selection_glow((w,h),'#28e4ff'),
                     (x1-8,y1-8,x2+8,y2+8),tags=('feedback','hover-glow'))

    def hit(self,event):
        if not hasattr(self,'scale'):return None
        x,y=(event.x-self.ox)/self.scale,(event.y-self.oy)/self.scale
        return next((key for key,(b,_) in self.items.items() if b[0]<=x<=b[2] and b[1]<=y<=b[3]),None)

    def click(self,event):
        self.canvas.focus_set();self.drag_origin=None;key=self.hit(event)
        if key:self.items[key][1]()
        elif self.in_title(event):self.begin_drag(event)

    def next_focus(self,event):
        keys=list(self.items);self.focus_index=keys[(keys.index(self.focus_index)+1)%len(keys)] if self.focus_index in keys else keys[0]
        self.set_hover(self.focus_index);return 'break'

    def activate_focus(self,event):
        if self.focus_index in self.items:self.items[self.focus_index][1]()
        return 'break'

if __name__=='__main__':
    try:ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError,OSError):pass
    GamerApp().mainloop()
