import telebot
import cv2
import numpy as np

def get_contour(image):

  #image = cv2.imread(image)

  hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  green_low = np.array([45 , 100, 50] )
  green_high = np.array([75, 255, 255])
  curr_mask = cv2.inRange(hsv_img, green_low, green_high)
  hsv_img[curr_mask > 0] = ([75,255,200])

  ## converting the HSV image to Gray inorder to be able to apply 
  ## contouring
  RGB_again = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
  gray = cv2.cvtColor(RGB_again, cv2.COLOR_RGB2GRAY)

  ret, threshold = cv2.threshold(gray, 90, 255, 0)

  contours, hierarchy =  cv2.findContours(threshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

  img = np.full((image.shape[0], image.shape[1], 3), 255, dtype=np.uint8) # create
  cv2.drawContours(img, contours, -1, (0, 0, 0), 3) 

  return img

bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты можешь отправить мне фотографию машины, а я обработаю её.\nДля ознакомления напиши help')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == ('help' or 'Help'):
        bot.send_message(message.chat.id, '1) Отправь мне фотографию, на которой есть машина\n2)Получай обработанную фотку :)\nВсё просто!')
    else:
        bot.send_message(message.chat.id, 'Ты можешь отправить мне фотографию машины, а я обработаю её.\nДля ознакомления напиши help')

@bot.message_handler(content_types=['photo'])
def send_photo(photo):
  
  img = preprocess_photo(photo)
  contoured_photo = get_contour(img)
  cv2.imwrite('image.jpg', contoured_photo)
  bot.send_photo(photo.chat.id, open("image.jpg", 'rb'))

def preprocess_photo(photo):
  fileID = photo.photo[-1].file_id
    
  file_info = bot.get_file(fileID)
   
  downloaded_file = bot.download_file(file_info.file_path)

  with open("image.jpg", 'wb') as new_file:
      new_file.write(downloaded_file)
  return cv2.imread("image.jpg") #open("image.jpg", 'rb') #downloaded_file

bot.delete_webhook()
bot.polling()
