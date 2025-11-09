import cv2
import mediapipe as mp
import textwrap


def putText_wrapped(image, text, top_left_corner, max_width, font, font_scale, color, thickness):
    """
    Draws text within a max width border by automatically wrapping lines.

    Args:
        image: The OpenCV image array.
        text: The string to draw.
        top_left_corner: (x, y) coordinates for the first line.
        max_width: The maximum width the text can occupy in pixels.
        ...other font parameters...
    """
    x, y = top_left_corner

    # Calculate the height of a single line of text and baseline
    (text_width, text_height), baseline = cv2.getTextSize("Sample Text", font, font_scale, thickness)
    line_height = text_height + baseline + 5  # Add some padding between lines

    # Use a loop to manually determine where to wrap the text.
    # We can use the standard 'textwrap' library for easy splitting into logical lines.

    # Estimate the maximum characters per line based on average width
    avg_char_width = text_width / len("Sample Text")
    max_chars_per_line = int(max_width / avg_char_width) - 2  # Subtracting a small buffer

    # Split the text into lines based on the calculated limit
    lines = textwrap.wrap(text, width=max_chars_per_line)

    # Draw each line sequentially
    for i, line in enumerate(lines):
        # Calculate the Y position for the current line
        # Start Y is the original Y + (line index * height per line)
        current_y = y + (i * line_height)

        # Ensure the Y position doesn't exceed image bounds (optional but recommended)
        if current_y > image.shape[0]:
            print(f"Warning: Text exceeded vertical bounds, stopping drawing early.")
            break

        # Draw the line
        cv2.putText(image, line, (x, current_y), font, font_scale, color, thickness, cv2.LINE_AA)



mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

hands = mp_hands.Hands()
text = "Touch Here"
org = (10, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
color = (0, 255, 0)
thickness = 2
lineType = cv2.LINE_AA

while True:
    data, image = cap.read()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # y 30 x 50
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        hand1 = results.multi_hand_landmarks[0]
        h, w, c = image.shape

        cx41 = int(hand1.landmark[4].x * w)
        cy41 = int(hand1.landmark[4].y * h)

        cx81 = int(hand1.landmark[8].x * w)
        cy81 = int(hand1.landmark[8].y * h)

        if cx81 < 200 and cy81 < 30:
            text = "Touching"
        else:
            text = "Touch Here"

        cv2.putText(image, text, org, font, fontScale, color, 1, lineType)

        if len(results.multi_hand_landmarks) >= 2:
            hand2 = results.multi_hand_landmarks[1]

            cx42 = int(hand2.landmark[4].x * w)
            cy42 = int(hand2.landmark[4].y * h)

            cx82 = int(hand2.landmark[8].x * w)
            cy82 = int(hand2.landmark[8].y * h)

            add_x = 20
            add_y = 30
            mid_text = "This is a message"
            min_org = min((cx41 + add_x, cy41 + add_y), (cx42 + add_x, cy42 + add_y), (cx81 + add_x, cy81 + add_y), (cx82 + add_x, cy82 + add_y))
            max_org = max((cx41 + add_x, cy41 + add_y), (cx42 + add_x, cy42 + add_y), (cx81 + add_x, cy81 + add_y), (cx82 + add_x, cy82 + add_y))
            max_w = max_org[0] - min_org[0]

            try:
                putText_wrapped(image, mid_text, min_org, max_w, font, fontScale, color, 1)
            except:
                pass

            cv2.line(image, (cx81, cy81), (cx82, cy82), color=(0, 255, 0), thickness=2)
            cv2.line(image, (cx81, cy81), (cx41, cy41), color=(0, 255, 0), thickness=2)
            cv2.line(image, (cx41, cy41), (cx42, cy42), color=(0, 255, 0), thickness=2)
            cv2.line(image, (cx82, cy82), (cx42, cy42), color=(0, 255, 0), thickness=2)

    cv2.imshow('Handtracker', image)
    cv2.waitKey(1)
