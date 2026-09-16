"""Internal pages drawn with the same controls as the main screen."""
from PIL import Image
from controller import APP_NAME, APP_VERSION, resource_path
from visuals import flag_plaque, round_flag
import startup

class Pages:
    def draw_folders(self):
        self.headline(self.ui('LOCAL DO JOGO','GAME FOLDERS','CARPETAS DEL JUEGO','SPIELORDNER'),self.ui('Escolhe o destino de cada efeito.','Choose the destination for each effect.','Elige el destino de cada efecto.','Wähle den Zielordner für jeden Effekt.'))
        for smoke,x in ((True,382),(False,1020)):
            self.glow((x,315,x+568,728))
            self.symbol('folder',x+36,349,48)
            title=self.ui('PASTA DO FUMO','SMOKE FOLDER','CARPETA DEL HUMO','RAUCHORDNER') if smoke else self.ui('PASTA DOS ESCAPES','EXHAUST FOLDER','CARPETA DEL ESCAPE','AUSPUFFORDNER')
            self.text_box((x+30,426,x+538,477),title,26,bold=True)
            self.text_box((x+30,485,x+538,520),'Forza Horizon 6' if smoke else 'MediaPC',27,'#4ce8ff',bold=True)
            path=self.game_root.get() if smoke else self.exhaust_path.get()
            self.text_box((x+30,544,x+538,612),path or self.ui('Pasta por selecionar','Folder not selected','Carpeta sin seleccionar','Ordner nicht ausgewählt'),17,'#a5bcd0')
            self.button('folder_'+str(smoke),(x+30,639,x+538,701),self.tr('PROCURAR'),lambda s=smoke:self.change_page('smoke_folder' if s else 'exhaust_folder'),size=19)

    def folder_caption(self,smoke):
        if smoke:return self.ui('Seleciona a pasta principal Forza Horizon 6.','Select the main Forza Horizon 6 folder.','Selecciona la carpeta principal Forza Horizon 6.','Wähle den Hauptordner Forza Horizon 6.')
        return self.ui('Seleciona a pasta MediaPC dentro da instalação do FH6.','Select the MediaPC folder inside the FH6 installation.','Selecciona la carpeta MediaPC dentro de la instalación de FH6.','Wähle den Ordner MediaPC innerhalb der FH6-Installation.')

    def draw_folder(self):
        smoke=self.page=='smoke_folder'
        title=self.ui('PASTA DO FUMO','SMOKE FOLDER','CARPETA DEL HUMO','RAUCHORDNER') if smoke else self.ui('PASTA DOS ESCAPES','EXHAUST FOLDER','CARPETA DEL ESCAPE','AUSPUFFORDNER')
        self.headline(title,self.folder_caption(smoke))
        self.glow((379,330,1598,713));self.symbol('folder',417,371,38)
        self.text_box((478,371,1548,424),'Forza Horizon 6' if smoke else 'MediaPC',27,bold=True)
        self.text_box((414,441,1553,488),r'…\steamapps\common\Forza Horizon 6'+('' if smoke else r'\MediaPC'),20,'#4ce8ff')
        self.entry_at(self.folder_entry,self.game_root if smoke else self.exhaust_path,(415,514,1250,560),18)
        self.button('pick',(1301,509,1557,568),self.tr('PROCURAR'),self.pick_module_folder,size=18)
        self.button('save',(1120,619,1557,680),self.ui('GUARDAR E VOLTAR','SAVE AND RETURN','GUARDAR Y VOLVER','SPEICHERN UND ZURÜCK'),self.save_module_folder,size=18)

    def draw_languages(self):
        self.headline('IDIOMA / LANGUAGE',self.tr('Escolhe o idioma. A escolha fica guardada automaticamente.'))
        languages=(('pt','PORTUGUÊS','PORTUGAL','#21eaff'),('en','ENGLISH','UNITED KINGDOM','#ff3d78'),('es','ESPAÑOL','ESPAÑA','#ffd447'),('fr','FRANÇAIS','FRANCE','#78a7ff'),('de','DEUTSCH','DEUTSCHLAND','#ff5a4f'))
        panel=(560,293,1450,881)
        self.canvas.create_rectangle(*self.coords(panel),fill='#040c19',outline='#173a59',width=max(1,round(self.scale)))
        self.canvas.create_line(*self.coords((584,337,1426,337)),fill='#1f6684',width=max(1,round(self.scale)))
        self.text_box((594,307,1415,333),'SELECT LANGUAGE',12,'#8aa9c3',bold=True,single_line=True)
        for i,(code,name,country,accent) in enumerate(languages):
            x=587;y=350+i*99;box=(x,y,1423,y+82);selected=self.language==code
            if selected:self.glow(box,True)
            else:self.canvas.create_rectangle(*self.coords(box),fill='#071323',outline='#24516d',width=max(1,round(self.scale)))
            flag_path=resource_path('assets/flags')/f'{code}.png'
            if flag_path.exists():
                flag=Image.open(flag_path)
                self.picture(('round-flag',code),round_flag(flag,(66,66),accent),(x+18,y+8,x+84,y+74))
            self.text_box((x+110,y+13,x+540,y+45),name,20,'#edf7ff',bold=True,single_line=True)
            self.text_box((x+110,y+47,x+540,y+69),country,11,'#87a3ba',bold=True,single_line=True)
            self.canvas.create_oval(*self.coords((x+695,y+34,x+705,y+44)),fill=accent,outline='')
            # The compact chevron/check indicator keeps the row clean at the
            # smallest supported window size; the flag and name carry the
            # language label, just like the reference panel.
            self.text_box((x+760,y+24,x+815,y+58),'✓' if selected else '›',18,accent,bold=True,align='right',valign='center',single_line=True)
            self.items['lang_'+code]=(box,lambda c=code:self.set_language(c))

    def draw_about(self):
        self.headline(self.tr('SOBRE A APLICAÇÃO'),f'{APP_NAME}  {APP_VERSION}  /  RICARDOSTONEPT')
        sections=[
          (self.ui('01  COR DO DRIFT','01  DRIFT COLOUR','01  COLOR DEL DERRAPE','01  DRIFTFARBE'),self.ui(
            'Escolhe uma cor e usa APLICAR NO JOGO. A poeira colorida deixa um rasto reforçado. RGB experimental aplica três efeitos: ciano, rosa e dourado. É uma combinação estática; a mistura visual precisa de teste no FH6. Reinicia o jogo após aplicar.',
            'Choose a colour and APPLY TO GAME. Coloured dust leaves a stronger trail. Experimental RGB applies three effects: cyan, pink and gold. This is a static mix; its appearance needs testing in FH6. Restart the game after applying.',
            'Elige un color y APLICAR AL JUEGO. El polvo coloreado deja un rastro reforzado. RGB experimental aplica tres efectos: cian, rosa y dorado. Es una mezcla estática pendiente de probar en FH6. Reinicia el juego después de aplicar.',
            'Wähle eine Farbe und IM SPIEL ANWENDEN. Farbiger Staub bildet eine stärkere Spur. Experimentelles RGB nutzt drei Effekte: Cyan, Pink und Gold. Statische Mischung; Darstellung in FH6 noch zu testen. Starte das Spiel danach neu.')),
          (self.ui('02  CORES DO ESCAPE','02  EXHAUST COLOURS','02  COLORES DEL ESCAPE','02  AUSPUFFFARBEN'),self.ui(
            'Escolhe um dos 18 cartões e usa APLICAR ESCAPE. São instalados os ficheiros de cor das chamas, incluindo combinações neon duplas. O efeito aparece quando o carro produz backfire. Esta opção não altera o som nem força chamas contínuas.',
            'Choose one of 18 cards and APPLY EXHAUST. The flame colour files include neon dual combinations. The effect appears when the car produces backfire. It does not change sound or force continuous flames.',
            'Elige una de las 18 tarjetas y APLICAR ESCAPE. Se instalan colores de llama, también combinaciones neon dobles. El efecto aparece con el backfire del coche. No cambia el sonido ni fuerza llamas continuas.',
            'Wähle eine der 18 Karten und AUSPUFF ANWENDEN. Installiert werden Flammenfarben, auch doppelte Neon-Kombinationen. Sichtbar bei Fehlzündungen; keine Tonänderung und keine erzwungenen Dauerflammen.')),
          (self.ui('03  ONDE INSTALAR','03  INSTALL LOCATION','03  DÓNDE INSTALAR','03  INSTALLATIONSORDNER'),self.ui(
            'Fumo: seleciona a pasta principal Forza Horizon 6.\nEscapes: seleciona a pasta MediaPC.\nOs destinos são guardados separadamente. Fecha o FH6, aplica cada efeito e volta a abrir o jogo.',
            'Smoke: select the main Forza Horizon 6 folder.\nExhaust: select MediaPC.\nFolders are saved separately. Close FH6, apply each effect, then reopen the game.',
            'Humo: carpeta principal Forza Horizon 6.\nEscape: carpeta MediaPC.\nSe guardan por separado. Cierra FH6, aplica cada efecto y vuelve a abrir el juego.',
            'Rauch: Hauptordner Forza Horizon 6.\nAuspuff: Ordner MediaPC.\nOrdner werden getrennt gespeichert. Schließe FH6, wende die Effekte an und starte das Spiel erneut.')),
          (self.ui('04  BACKUP E RESTAURO','04  BACKUP AND RESTORE','04  COPIA Y RESTAURACIÓN','04  SICHERUNG UND WIEDERHERSTELLUNG'),self.ui(
            'Os ficheiros existentes são guardados antes da substituição. RESTAURAR ORIGINAL recupera os efeitos anteriores. Quando a app criou um ficheiro novo, o restauro remove essa cópia. Fecha o jogo antes de restaurar.',
            'Existing files are backed up before replacement. RESTORE ORIGINAL recovers previous effects. Files newly created by the app are removed during restore. Close the game before restoring.',
            'Los archivos existentes se guardan antes de sustituirlos. RESTAURAR ORIGINAL recupera los efectos anteriores y elimina las copias nuevas creadas por la app. Cierra el juego antes de restaurar.',
            'Vorhandene Dateien werden vor dem Ersetzen gesichert. ORIGINAL WIEDERHERSTELLEN stellt frühere Effekte wieder her und entfernt neu angelegte Kopien. Schließe das Spiel vor dem Wiederherstellen.'))]
        for i,(title,body) in enumerate(sections):
            row,col=divmod(i,2);x=382+col*638;y=300+row*283
            self.rgb_frame((x,y,x+568,y+254))
            self.glow((x,y,x+568,y+254))
            self.text_box((x+26,y+25,x+542,y+63),title,21,'#46e7f0',bold=True)
            self.text_box((x+26,y+81,x+542,y+230),body,21)

    def draw_sizes(self):
        from app import SIZES
        self.headline(self.ui('TAMANHO DA APP','APP SIZE','TAMAÑO DE LA APP','APP-GRÖSSE'),self.ui('Escolhe o tamanho. A app guarda a tua preferência.','Choose a size. The app remembers your preference.','Elige un tamaño. La app guarda tu preferencia.','Wähle eine Größe. Die App speichert deine Auswahl.'))
        names={'small':self.ui('PEQUENO','SMALL','PEQUEÑO','KLEIN'),'medium':self.ui('MÉDIO','MEDIUM','MEDIANO','MITTEL'),'large':self.ui('GRANDE','LARGE','GRANDE','GROSS'),'screen':self.ui('AJUSTAR AO ECRÃ','FIT SCREEN','AJUSTAR A PANTALLA','AN BILDSCHIRM ANPASSEN')}
        for i,key in enumerate(names):
            row,col=divmod(i,2);x=382+col*638;y=322+row*231
            label=names[key]
            if key in SIZES:label+=f'\n{SIZES[key][0]} × {SIZES[key][1]}'
            self.button('size_'+key,(x,y,x+568,y+177),label,lambda k=key:self.resize_choice(k),icon='size',selected=self.size_choice==key,size=27)

    def draw_startup(self):
        self.headline(self.ui('ARRANQUE COM O WINDOWS','WINDOWS STARTUP','INICIO CON WINDOWS','WINDOWS-AUTOSTART'))
        self.glow((382,298,1588,758));self.symbol('windows',420,341,47)
        self.text_box((490,330,1539,435),self.ui('Abre a app automaticamente quando iniciares sessão no Windows.','Open the app automatically when you sign in to Windows.','Abre la app automáticamente al iniciar sesión en Windows.','Öffne die App automatisch bei der Windows-Anmeldung.'),25,bold=True)
        try:active=startup.enabled()
        except OSError:active=False
        self.text_box((422,459,1540,506),self.ui('ATIVADO','ENABLED','ACTIVADO','AKTIVIERT') if active else self.ui('DESATIVADO','DISABLED','DESACTIVADO','DEAKTIVIERT'),21,'#4ce8ff',bold=True)
        self.button('enable',(418,538,935,603),self.ui('ATIVAR','ENABLE','ACTIVAR','AKTIVIEREN'),lambda:self.set_startup(True),selected=active,size=21)
        self.button('disable',(1013,538,1550,603),self.ui('DESATIVAR','DISABLE','DESACTIVAR','DEAKTIVIEREN'),lambda:self.set_startup(False),selected=not active,size=21)
        self.text_box((420,635,1545,717),self.ui('Guarda a app numa pasta definitiva antes de ativar. Se a moveres, ativa de novo. Esta opção abre apenas a app.',
          'Keep the app in its permanent folder before enabling. Enable again if you move it. This option only opens the app.',
          'Guarda la app en una carpeta definitiva antes de activar. Activa de nuevo si la mueves. Esta opción solo abre la app.',
          'Lege die App vor dem Aktivieren dauerhaft ab. Nach dem Verschieben erneut aktivieren. Diese Option öffnet nur die App.'),19,'#adc5d9')
        if self.startup_note:self.text_box((402,801,1560,862),self.startup_note,18,'#ffc979')
