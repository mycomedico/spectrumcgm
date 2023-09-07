# File name: settings.py
from kivy.app import App
from kivy.properties import NumericProperty,StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen



class SettingsScreen(Screen):
    brightness = NumericProperty(50)
    no_bulb = BooleanProperty(False)
    back_arr = u'\u2190'
    #back_arr = u'\u2612'
    #gear = u'\u2699'
    #exit = u'\u2612'

    #for some reason it's seeing a bulb object
    def on_pre_enter(self):
        if not self.manager.bulb_obj:
            self.manager.bulb_err = ''
            self.no_bulb = True
        else:
            try:
                self.brightness = self.manager.bulb_obj.get_properties()['bright']
            except Exception as e:
                self.manager.bulb_err = repr(e)
            else:
                self.manager.bulb_err = ''
                self.no_bulb = False

    def adjustbrightness(self,value):
        if self.manager.bulb_obj:
            try:
                self.manager.bulb_obj.set_brightness(value)
            except Exception as e:
                self.manager.bulb_err = repr(e)
            else:
                self.manager.bulb_err = ''

    def clear_user(self):
        app = App.get_running_app()
        app.config.read(app.get_application_config())
        app.config.remove_section('user')
        app.config.write()