import base64
from io import BytesIO
from pic2str import iconPBM
from PIL import Image, ImageQt

# Загрузка байтовых данных
byte_data = base64.b64decode(iconPBM)
image_data = BytesIO(byte_data)
image = Image.open(image_data)

# PIL в QPixmap
qImage = ImageQt.ImageQt(image)