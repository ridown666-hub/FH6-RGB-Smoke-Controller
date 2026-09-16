"""Code-drawn UI surfaces. Text and hit targets are rendered by the app."""
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

RGB_STOPS = ((0, 229, 255), (92, 89, 255), (255, 42, 190),
             (255, 107, 24), (155, 255, 45), (0, 229, 255))

def rgb_glow(size, selected=False):
    """Transparent cyan/magenta/rainbow edge used for titles and panels."""
    w, h = size
    pad = max(6, min(14, round(min(w, h) * .06)))
    full = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gradient = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for x in range(w):
        pos = x / max(1, w - 1) * (len(RGB_STOPS) - 1)
        i = min(int(pos), len(RGB_STOPS) - 2); t = pos - i
        c = tuple(int(RGB_STOPS[i][k] * (1-t) + RGB_STOPS[i+1][k] * t) for k in range(3))
        gd.line((x, 0, x, h), fill=c + (255,))
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((pad, pad, w-pad-1, h-pad-1), radius=max(9, pad),
                         outline=255, width=3 if selected else 2)
    blur = mask.filter(ImageFilter.GaussianBlur(9 if selected else 6))
    blur = blur.point(lambda a: min(190 if selected else 110, int(a * (1.7 if selected else 1.2))))
    aura = gradient.copy(); aura.putalpha(blur)
    full.alpha_composite(aura)
    edge = gradient.copy(); edge.putalpha(mask)
    full.alpha_composite(edge)
    return full

def clean_active_frame(size):
    """Single cyan-to-magenta active sidebar frame, without an inner edge."""
    w, h = size
    pad = max(3, min(7, round(min(w, h) * .045)))
    full = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    panel = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((pad, pad, w-pad-1, h-pad-1), radius=max(8, pad+4), fill=(4, 10, 24, 238))
    full.alpha_composite(panel)
    gradient = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    stops=((0,229,255),(92,89,255),(255,42,190))
    for x in range(w):
        pos=x/max(1,w-1)*(len(stops)-1); i=min(int(pos),len(stops)-2); t=pos-i
        c=tuple(int(stops[i][k]*(1-t)+stops[i+1][k]*t) for k in range(3))
        gd.line((x,0,x,h),fill=c+(255,))
    mask=Image.new('L',(w,h),0);md=ImageDraw.Draw(mask)
    md.rounded_rectangle((pad,pad,w-pad-1,h-pad-1),radius=max(8,pad+4),outline=255,width=2)
    aura=mask.filter(ImageFilter.GaussianBlur(5));aura=aura.point(lambda a:min(200,int(a*1.7)))
    glow=gradient.copy();glow.putalpha(aura);full.alpha_composite(glow)
    edge=gradient.copy();edge.putalpha(mask);full.alpha_composite(edge)
    return full

def rgb_text(size, text, font_size=30, glow=True):
    """Render a compact RGB title: the colour belongs to the letters."""
    w, h = size
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if not text or w < 2 or h < 2:
        return out
    font_candidates = (
        'C:/Windows/Fonts/segui zib.ttf',
        'C:/Windows/Fonts/seguisbi.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    )
    font = None
    for path in font_candidates:
        try:
            font = ImageFont.truetype(path, max(10, int(font_size)))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    bbox = md.textbbox((0, 0), text, font=font, stroke_width=1)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while tw > w - 18 and font_size > 12:
        font_size -= 1
        for path in font_candidates:
            try:
                font = ImageFont.truetype(path, max(10, int(font_size)))
                break
            except OSError:
                continue
        bbox = md.textbbox((0, 0), text, font=font, stroke_width=1)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = 9
    y = max(0, round((h - th) / 2) - bbox[1])
    md.text((x, y), text, font=font, fill=255, stroke_width=1, stroke_fill=255)
    gradient = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for px in range(w):
        pos = px / max(1, w - 1) * (len(RGB_STOPS) - 1)
        i = min(int(pos), len(RGB_STOPS) - 2)
        t = pos - i
        c = tuple(int(RGB_STOPS[i][k] * (1-t) + RGB_STOPS[i+1][k] * t) for k in range(3))
        gd.line((px, 0, px, h), fill=c + (255,))
    if glow:
        aura_mask = mask.filter(ImageFilter.GaussianBlur(8))
        aura_mask = aura_mask.point(lambda a: min(150, int(a * .9)))
        aura = gradient.copy(); aura.putalpha(aura_mask)
        out.alpha_composite(aura)
    gradient.putalpha(mask)
    out.alpha_composite(gradient)
    return out

def rgb_halo(size, text, font_size=30):
    """Soft RGB illumination for an existing baked logo.

    Only the blurred colour aura is returned, so the original logo remains
    crisp and is not duplicated by a second solid wordmark.
    """
    image = rgb_text(size, text, font_size, glow=False)
    alpha = image.getchannel('A').filter(ImageFilter.GaussianBlur(9))
    alpha = alpha.point(lambda a: min(135, int(a * .8)))
    image.putalpha(alpha)
    return image

def red_lights_glow(size, centers=((1168, 495), (1245, 495), (1488, 505), (1538, 505))):
    """Soft red bloom placed over the GTR's four rear lights.

    The artwork already contains the red lamps; this transparent overlay only
    adds a restrained luminous spill so it reads like an illuminated car light
    without covering the photograph or the controls.
    """
    w, h = size
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for cx, cy in centers:
        halo = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse((cx-44, cy-30, cx+44, cy+30), fill=(255, 20, 24, 66))
        halo = halo.filter(ImageFilter.GaussianBlur(18))
        out.alpha_composite(halo)
        core = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(core)
        cd.ellipse((cx-17, cy-12, cx+17, cy+12), fill=(255, 38, 30, 80))
        core = core.filter(ImageFilter.GaussianBlur(5))
        out.alpha_composite(core)
    return out

def neon_button(size, selected=False):
    w,h=size
    # Padding reserves room for the halo outside the actual hit box.
    p=12; W=w+2*p; H=h+2*p
    grad=Image.new('RGBA',(W,H))
    draw=ImageDraw.Draw(grad)
    for x in range(W):
        t=x/max(1,W-1)
        draw.line((x,0,x,H),fill=(int(18+218*t),int(233-183*t),255,255),width=1)
    mask=Image.new('L',(W,H)); d=ImageDraw.Draw(mask)
    d.rounded_rectangle((p,p,W-p-1,H-p-1),radius=10,outline=255,width=2 if not selected else 3)
    glow=mask.filter(ImageFilter.GaussianBlur(5 if selected else 3))
    glow=glow.point(lambda a:min(255,int(a*2.8)))
    output=grad.copy(); output.putalpha(glow)
    inner=Image.new('RGBA',(W,H)); di=ImageDraw.Draw(inner)
    di.rounded_rectangle((p,p,W-p-1,H-p-1),radius=10,fill=(4,10,24,230))
    output.alpha_composite(inner)
    # A shallow reflection makes the face read as glass.
    sheen=Image.new('RGBA',(W,H)); ds=ImageDraw.Draw(sheen)
    ds.rounded_rectangle((p+3,p+3,W-p-4,p+int(h*.48)),radius=7,fill=(105,132,205,20))
    output.alpha_composite(sheen)
    edge=grad.copy();edge.putalpha(mask);output.alpha_composite(edge)
    return output

def card_surface(source,size,color):
    w,h=size
    result=Image.new('RGBA',size,(3,8,16,235))
    # Exact source proportions are retained; crop to the thumbnail area.
    thumb=ImageOps.fit(source.convert('RGB'),(w-4,h-28),method=Image.Resampling.LANCZOS)
    result.paste(thumb,(2,2))
    d=ImageDraw.Draw(result)
    d.rectangle((1,h-27,w-2,h-1),fill=(3,9,17,245))
    d.line((2,h-28,w-3,h-28),fill=color,width=1)
    mask=Image.new('L',size);ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=10,fill=255)
    result.putalpha(mask)
    ImageDraw.Draw(result).rounded_rectangle((0,0,w-1,h-1),radius=10,outline=color,width=2)
    return result

def selection_glow(size,color):
    """Transparent neon halo used around selected colour cards."""
    w,h=size; pad=9
    if isinstance(color,str):
        color=tuple(int(color[i:i+2],16) for i in (1,3,5)) if color.startswith('#') else (60,220,255)
    base=Image.new('RGBA',(w+2*pad,h+2*pad),(0,0,0,0))
    ring=Image.new('RGBA',base.size,(0,0,0,0)); d=ImageDraw.Draw(ring)
    d.rounded_rectangle((pad,pad,w+pad-1,h+pad-1),radius=11,outline=color,width=3)
    halo=ring.getchannel('A').filter(ImageFilter.GaussianBlur(7))
    halo=halo.point(lambda a:min(210,int(a*2.6)))
    glow=Image.new('RGBA',base.size,color+(0,));glow.putalpha(halo)
    base.alpha_composite(glow);base.alpha_composite(ring)
    return base

def flag_plaque(flag,size,accent='#7a96b9'):
    """Display an unchanged flag in a lit gamer frame."""
    w,h=size
    image=Image.new('RGBA',size)
    d=ImageDraw.Draw(image)
    if isinstance(accent,str) and accent.startswith('#'):
        accent=tuple(int(accent[i:i+2],16) for i in (1,3,5))
    halo=Image.new('RGBA',size,(0,0,0,0));hd=ImageDraw.Draw(halo)
    hd.rounded_rectangle((2,2,w-3,h-3),radius=12,outline=accent+(120,),width=3)
    halo=halo.filter(ImageFilter.GaussianBlur(4))
    image.alpha_composite(halo)
    d=ImageDraw.Draw(image)
    d.rounded_rectangle((0,0,w-1,h-1),radius=12,fill=(5,12,25,255),outline=accent+(220,),width=2)
    d.rounded_rectangle((7,7,w-8,h-8),radius=8,outline=(140,170,205,130),width=1)
    flag=ImageOps.contain(flag.convert('RGBA'),(w-20,h-20),Image.Resampling.LANCZOS)
    image.alpha_composite(flag,((w-flag.width)//2,(h-flag.height)//2))
    # Reflected light belongs to the display glass, not to the flag artwork.
    glass=Image.new('RGBA',size);g=ImageDraw.Draw(glass)
    g.polygon(((9,9),(w-9,9),(w-9,h*.25),(9,h*.68)),fill=(255,255,255,30))
    g.line((12,h-13,w-13,h-13),fill=accent+(150,),width=2)
    image.alpha_composite(glass)
    d=ImageDraw.Draw(image);d.line((13,3,w-14,3),fill=accent+(235,),width=1)
    for cx in (10,w-11):
        d.ellipse((cx-2,10,cx+2,14),fill=accent+(220,))
    return image

def round_flag(flag, size, accent='#21eaff'):
    """Circular language badge with a restrained neon rim."""
    w, h = size
    side = max(1, min(w, h))
    image = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    if isinstance(accent, str) and accent.startswith('#'):
        accent = tuple(int(accent[i:i+2], 16) for i in (1, 3, 5))
    halo = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((4, 4, side-5, side-5), outline=accent+(150,), width=3)
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(5)))
    rim = ImageDraw.Draw(image)
    rim.ellipse((2, 2, side-3, side-3), fill=(5, 12, 24, 255), outline=accent+(235,), width=2)
    fitted = ImageOps.fit(flag.convert('RGBA'), (side-10, side-10), Image.Resampling.LANCZOS)
    mask = Image.new('L', fitted.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, fitted.width-1, fitted.height-1), fill=255)
    fitted.putalpha(mask)
    image.alpha_composite(fitted, ((side-fitted.width)//2, (side-fitted.height)//2))
    shine = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.pieslice((7, 7, side-8, side-8), 195, 325, fill=(255, 255, 255, 42))
    image.alpha_composite(shine)
    return image
