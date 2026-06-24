from PIL import Image
import qrcode
from io import BytesIO
# def create_qr_code(data:str)->BytesIO:
#     qr = qrcode.QRCode(
#         version = 1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit= True)
#     img = qr.make_image(fill_color="black",back_color="white")
#     buffer = BytesIO()
#     img.save(buffer,format="PNG")
#     buffer.seek(0)
#     return buffer


def create_qr_code(data: str ,fg_color : str ="black",bg_color:str = "white",logo_bytes:  bytes =None) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color = fg_color,back_color=bg_color).convert("RGBA")
    if logo_bytes:
        logo = Image.open(BytesIO(logo_bytes)).convert("RGBA")
        basewidth = int(float(img.size[0])/4)   
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth,hsize),Image.Resampling.LANCZOS)

        pos = ((img.size[0]-logo.size[0])//2,(img.size[1]-logo.size[1])//2)
        img.paste(logo,pos,logo)
    buffer = BytesIO()
    img.save(buffer,format="PNG")
    buffer.seek(0)
    return buffer

    
    
    
    