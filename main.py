import telebot
import cv2 as cv
import numpy as np

# параметры цветового фильтра
hsv_min = np.array((2, 28, 65), np.uint8)
hsv_max = np.array((26, 238, 255), np.uint8)


def get_contour(img):
    # hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #
    # green_low = np.array([45, 100, 50])
    # green_high = np.array([75, 255, 255])
    # curr_mask = cv2.inRange(hsv_img, green_low, green_high)
    # hsv_img[curr_mask > 0] = ([75, 255, 200])
    #
    # ## converting the HSV image to Gray inorder to be able to apply
    # ## contouring
    # RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
    # gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)
    #
    # ret, threshold = cv2.threshold(gray, 90, 255, 0)
    #
    # contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #
    # img = np.full((image.shape[0], image.shape[1], 3), 255, dtype=np.uint8)  # create
    # cv2.drawContours(img, contours, -1, (0, 0, 0), 3)

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
    thresh = cv.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
    # ищем контуры и складируем их в переменную contours
    contours, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # отображаем контуры поверх изображения
    cv.drawContours(img, contours, -1, (255, 0, 0), 3, cv.LINE_AA, hierarchy, 1)
    return img


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
