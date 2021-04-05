import os
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
import shutil

try:
    from PIL import Image
except ImportError:
    pass

app_folder = os.path.dirname(os.path.abspath(__file__))
storage = os.path.join(app_folder, 'Data.json')


# Создание трёх экранов, наследуемых от базового
class MainScreen(Screen):
    pass


class AddContactScreen(Screen):
    pass


class UpdateContactScreen(Screen):
    pass


class CameraScreen(Screen):
    pass


class ViewContactScreen(Screen):
    pass


# Добавление менеджера и трёх кастомных экранов
sm = ScreenManager()
sm.add_widget(MainScreen(name='MainScreen'))
sm.add_widget(AddContactScreen(name='AddContactScreen'))
sm.add_widget(UpdateContactScreen(name='UpdateContactScreen'))
sm.add_widget(CameraScreen(name='CameraScreen'))
sm.add_widget(ViewContactScreen(name='ViewContactScreen'))


class SwipeToDeleteItem(MDCardSwipe):
    type_swipe = "hand"
    name = StringProperty()
    phone = StringProperty()
    email = StringProperty()
    img_source = StringProperty()


class MyApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__()
        # Создание списка выполненных заданий для отслеживания
        self.style = Builder.load_file('style.kv')
        self.camera = self.style.get_screen('CameraScreen').ids.camera_box.ids.camera
        # self.camera.remove_widget(self.camera.children[0])
        self.camera.on_picture_taken = self.picture_taken
        self.screen_history = []

    def build(self):
        # Активация разметки
        return self.style

    def save_data(self):
        save_list = self.style.get_screen('MainScreen').ids.my_list.children[::-1]
        store = JsonStore(storage)
        store.clear()
        for item in save_list:
            if isinstance(item, SwipeToDeleteItem):
                store.put(str(item),
                          contact_name=item.name,
                          phone=item.phone,
                          email=item.email,
                          photo=item.img_source)

    def load_data(self):
        store = JsonStore(storage)
        if store.count() > 0:
            for key in store:
                item = SwipeToDeleteItem(
                    name=store[key]['contact_name'],
                    phone=store[key]['phone'],
                    email=store[key]['email'],
                    img_source=store[key]['photo']
                )
                self.style.get_screen('MainScreen').ids.my_list.add_widget(
                    item
                )

    def on_start(self):
        try:
            self.load_data()
        except FileNotFoundError:
            pass
        super().on_start()

    def on_stop(self):
        self.save_data()
        super().on_stop()

    def on_pause(self):
        self.save_data()
        return super().on_pause()

    def on_resume(self):
        super().on_resume()

    def change_screen(self, screen):
        self.screen_history.append(screen)
        # Функция перехода на экран screen
        self.root.current = screen

    def on_previous_screen(self):
        self.root.current = self.screen_history[self.screen_history.index('CameraScreen') - 1]
        self.screen_history.remove('CameraScreen')

    def addContact(self):
        # Функция добавления задания в список
        # Считывание данных из экрана добавления
        input_name = self.style.get_screen('AddContactScreen').ids.input_name.text
        input_phone = self.style.get_screen('AddContactScreen').ids.input_phone.text
        input_email = self.style.get_screen('AddContactScreen').ids.input_email.text
        input_photo = self.style.get_screen('AddContactScreen').ids.icon_id.source
        # Если данные введены
        if input_name.split() and input_phone.split() and input_email.split():
            if input_photo:
                # Добавление записи
                self.style.get_screen('MainScreen').ids.my_list.add_widget(
                    SwipeToDeleteItem(name=input_name,
                                      phone=input_phone,
                                      email=input_email,
                                      img_source=input_photo)
                )
                # Переход на стартовый экран
                self.change_screen('MainScreen')
                # Очистка данных на экране ввода
                self.style.get_screen('AddContactScreen').ids.input_name.text = ""
                self.style.get_screen('AddContactScreen').ids.input_phone.text = ""
                self.style.get_screen('AddContactScreen').ids.input_email.text = ""
                self.style.get_screen('AddContactScreen').ids.icon_id.source = ""
            else:
                Snackbar(text='Take the photo)').show()
        # Если нет
        else:
            # Показываем уведомление о пустом поле ввода
            Snackbar(text='Enter the value').show()

    def viewContact(self, instance):
        self.updating_item = instance
        self.style.get_screen('ViewContactScreen').ids.contact_name.text = 'Name: ' + self.updating_item.name
        self.style.get_screen('ViewContactScreen').ids.contact_phone.text = 'Phone: ' + self.updating_item.phone
        self.style.get_screen('ViewContactScreen').ids.contact_email.text = 'Email: ' + self.updating_item.email
        self.style.get_screen('ViewContactScreen').ids.contact_photo.source = self.updating_item.img_source
        self.change_screen('ViewContactScreen')

    def updateContactStart(self):
        # Функция перехода на экран обновления и передача в него элемента
        self.style.get_screen('ViewContactScreen').ids.contact_name.text = ''
        self.style.get_screen('ViewContactScreen').ids.contact_phone.text = ''
        self.style.get_screen('ViewContactScreen').ids.contact_email.text = ''

        self.style.get_screen('UpdateContactScreen').ids.update_input_name.text = self.updating_item.name
        self.style.get_screen('UpdateContactScreen').ids.update_input_phone.text = self.updating_item.phone
        self.style.get_screen('UpdateContactScreen').ids.update_input_email.text = self.updating_item.email
        self.style.get_screen('UpdateContactScreen').ids.update_icon_id.source = self.updating_item.img_source
        self.change_screen('UpdateContactScreen')

    def updateContactFinish(self):
        # # Функция обновления задания в списке
        update_input_name = self.style.get_screen('UpdateContactScreen').ids.update_input_name.text
        update_input_phone = self.style.get_screen('UpdateContactScreen').ids.update_input_phone.text
        update_input_email = self.style.get_screen('UpdateContactScreen').ids.update_input_email.text
        update_input_photo = self.style.get_screen('UpdateContactScreen').ids.update_icon_id.source
        # Если данные введены
        if update_input_name.split() and update_input_phone.split() and update_input_email.split():
            if update_input_photo.split():
                self.updating_item.name = update_input_name
                self.updating_item.phone = update_input_phone
                self.updating_item.email = update_input_email
                self.updating_item.img_source = update_input_photo
            else:
                self.updating_item.name = update_input_name
                self.updating_item.phone = update_input_phone
                self.updating_item.email = update_input_email
            # Переход на стартовый экран

            # Очистка данных на экране ввода
            self.style.get_screen('UpdateContactScreen').ids.update_input_name.text = ""
            self.style.get_screen('UpdateContactScreen').ids.update_input_phone.text = ""
            self.style.get_screen('UpdateContactScreen').ids.update_input_email.text = ""
            self.style.get_screen('UpdateContactScreen').ids.update_icon_id.source = ""
            self.style.get_screen('AddContactScreen').ids.icon_id.source = ""
            self.change_screen('MainScreen')
        # Если нет
        else:
            # Показываем уведомление о пустом поле ввода
            Snackbar(text='Enter the value').show()

    def remove_contact(self):
        self.style.get_screen('MainScreen').ids.my_list.remove_widget(self.updating_item)
        self.change_screen('MainScreen')

    def open_camera(self):
        self.change_screen('CameraScreen')

    def take_photo(self):
        self.camera.shoot()

    def picture_taken(self, filename):
        img_src = app_folder + '/photos/' + filename

        try:
            shutil.move(filename, img_src)
        except FileNotFoundError:
            os.makedirs(app_folder + '/photos')
            shutil.move(filename, img_src)

        try:
            img = Image.open(img_src)
            img = img.rotate(-90, Image.NEAREST, expand=1)
            img.save(img_src)
        except Exception:
            pass

        self.style.get_screen('AddContactScreen').ids.icon_id.source = img_src
        # self.style.get_screen('AddContactScreen').ids.to_rotate.rotation = -90
        # # self.style.get_screen('UpdateContactScreen').ids.to_rotate.rotation = -90
        self.style.get_screen('UpdateContactScreen').ids.update_icon_id.source = img_src
        self.on_previous_screen()


MyApp().run()
