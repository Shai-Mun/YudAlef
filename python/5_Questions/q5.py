from PIL import Image
import cv2
import numpy as np

img_name = "dog.jpg"
img = Image.open(img_name)
color = ' .;-:!>7?CO$QHNM'
pixel = img.load()
new_Pic = ""

for y in range(img.height):
    for x in range(img.width):
        rgb = pixel[x,y]
        avg = (rgb[0] + rgb[1] + rgb[2])/3
        new_Pic += color[int(avg/16)]
    new_Pic += "\n"

print(new_Pic)


# Function to render ASCII characters on a blank image
def string_to_image(ascii_string, font_scale=1, thickness=1, text_color=(0, 0, 0)):
    # Split the ASCII string into rows
    rows = ascii_string.split('\n')

    # Calculate the size of the image (width = max line length, height = number of lines)
    max_line_length = max(len(line) for line in rows)
    height = len(rows) * 5  # 30 is an arbitrary height per row (font size)
    width = max_line_length * 4  # 20 is an arbitrary width per character

    # Create a blank white image
    image = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

    # Set font style
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Loop through the rows and characters and render each character on the image
    y_offset = 3  # Start from the top of the image
    for row in rows:
        x_offset = 1  # Start from the left of the image
        for char in row:
            # Render each character as text on the image
            cv2.putText(image, char, (x_offset, y_offset), font, font_scale, text_color, thickness)
            x_offset += 4  # Move to the next character position (spacing between characters)
        y_offset += 5  # Move down to the next row

    return image

cap = cv2.VideoCapture('jump.mp4')
v_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
v_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:

        v_frame = ""
        info = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        color = ' .;-:!>7?CO$QHNM'

        for y in range(v_height):
            for x in range(v_width):
                rgb = info[y, x]
                avg = (rgb[0] + rgb[1] + rgb[2]) // 3
                v_frame += color[avg // 16]
            v_frame += "\n"

        img = string_to_image(v_frame)
        cv2.imshow('ASCII Art Image', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
