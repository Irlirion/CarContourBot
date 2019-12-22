import telebot
import cv2 as cv
import numpy as np


def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
 
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv.Canny(image, lower, upper)
 
	# return the edged image
	return edged

def get_contour(img):
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(5,5),1000)
    _, thresh = cv.threshold(gray,80,255,cv.THRESH_BINARY)

    # Find contours
    edged=auto_canny(thresh)
    contours, _ = cv.findContours(edged,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv.contourArea,reverse=True) 

    # Select long perimeters only
    perimeters = [cv.arcLength(contour,True) for contour in contours]

    # Show image
    imgcont = np.full((img.shape[0], img.shape[1], 3), 255, dtype=np.uint8)  # create
    [cv.drawContours(imgcont, [contours[i]], 0, (0,0,0), 2) for i, perimeter in enumerate(perimeters) if perimeter > perimeters[0] / 8]

    return imgcont


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Привет, ты можешь отправить мне фотографию машины, а я обработаю её.\nДля ознакомления напиши help')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == ('help' or 'Help'):
        bot.send_message(message.chat.id,
                         '1) Отправь мне фотографию, на которой есть машина\n2)Получай обработанную фотку :)\nВсё просто!')
    else:
        bot.send_message(message.chat.id,
                         'Ты можешь отправить мне фотографию машины, а я обработаю её.\nДля ознакомления напиши help')


@bot.message_handler(content_types=['photo'])
def send_photo(photo):
    img = preprocess_photo(photo)
    contoured_photo = get_contour(img)
    cv.imwrite('image.jpg', contoured_photo)
    bot.send_photo(photo.chat.id, open("image.jpg", 'rb'))


def preprocess_photo(photo):
    fileID = photo.photo[-1].file_id

    file_info = bot.get_file(fileID)

    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    return cv.imread("image.jpg")  # open("image.jpg", 'rb') #downloaded_file


bot.delete_webhook()
bot.polling()
