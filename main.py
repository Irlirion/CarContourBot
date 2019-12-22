!pip install pyTelegramBotAPI
import telebot
import cv2 as cv
import numpy as np

# параметры цветового фильтра
hsv_min = np.array((2, 28, 65), np.uint8)
hsv_max = np.array((26, 238, 255), np.uint8)


def get_contour(img):
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(1,1),1000)
    flag, thresh = cv.threshold(blur, 70, 255, cv.THRESH_BINARY)
    edged=cv.Canny(thresh,30,200)
    # Find contours
    contours, hierarchy = cv.findContours(edged,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv.contourArea,reverse=True) 
    # Select long perimeters only
    perimeters = [cv.arcLength(contours[i],True) for i in range(len(contours))]
    listindex=[i for i in range(int(len(perimeters)/3)) if perimeters[i]>perimeters[0]/4]
    # Show image
    imgcont = np.full((img.shape[0], img.shape[1], 3), 255, dtype=np.uint8)  # create
    [cv.drawContours(imgcont, [contours[i]], 0, (0,0,0), 5) for i in listindex]

    return imgcont


bot = telebot.TeleBot('911809193:AAFhLS5-OSKrYaX0NcWV5V6N5bX1asfrACc')


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
