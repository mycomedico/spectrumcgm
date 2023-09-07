# File name: main.py
# modified from https://gist.github.com/Cheaterman/812203a74f8c552a4918?permalink_comment_id=2623631
#v2 animate background
#v2 store token until expiration
#from kivy.config import Config
#Config.set('graphics','width','360')
#Config.set('graphics','height','760')
import kivy
import configparser
from kivy.app import App
from tendo import singleton
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, BooleanProperty
from plyer import keystore
from pydexcom import Dexcom
from pylibre import Libre
from yeelight import Bulb
from datetime import datetime
#from kivy.clock import Clock

kivy.require('2.1.0')


Builder.load_file('login.kv')
Builder.load_file('lightconfig.kv')
Builder.load_file('sweetlight.kv')
Builder.load_file('settings.kv')



class Spectrum(ScreenManager):

    username = StringProperty('')
    password = StringProperty('')
    email = StringProperty('')
    cgm = StringProperty('')
    location = StringProperty('')
    current_bg = StringProperty('')
    current_bg_mmol = StringProperty('')
    bulb = StringProperty('')
    bulb_err = StringProperty('')
    trend_arr = StringProperty('')
    cgm_err = StringProperty('')
    units_mmol = BooleanProperty(False)

    mins_since_last_reading = NumericProperty(0)
    red = NumericProperty(0)
    green = NumericProperty(0)
    blue = NumericProperty(0)
    alpha = NumericProperty(1)
    urgent = NumericProperty(40)
    low = NumericProperty(90)
    normal = NumericProperty(120)
    elevated = NumericProperty(170)
    high = NumericProperty(250)
    super_high = NumericProperty(400)
    color_max = NumericProperty(255)
    color_min = NumericProperty(0)

    bulb_obj = ObjectProperty(None)
    last_reading = ObjectProperty(None)
    libreconnection = ObjectProperty(None)

    label_color = ListProperty([0, 0, 0, 1])

    def on_kv_post(self, base_widget):
        app = App.get_running_app()
        if not app.user_exists:
            self.transition = NoTransition()
            self.current = 'login'
            #self.current = 'lightconfig'
            #self.current = 'settingsscreen'
        else:
            #load all user values and check bg
            app.config.read(app.get_application_config())
            self.username = app.config.get('user','username')
            self.cgm = app.config.get('user', 'cgm')
            self.location = app.config.get('user', 'location')
            try:
                self.bulb = app.config.get('user', 'bulb')
                if self.bulb != '-1':
                    self.bulb_obj = Bulb(self.bulb)
                    self.bulb_obj.turn_on()
            except:
                self.bulb = '-1'

            # go to login screen if password not there
            try:
                self.password = keystore.get_key('spectrumcgm', self.username)
            except:
                #maybe i should reset all values here? otherwise login populated
                self.current = 'login'
                return

            else:
                if self.cgm == 'dexcom':
                    self.get_dex_bg()
                    if self.cgm_err == '':
                        self.current = 'sweetlight'
                    else:
                        self.current = 'login'
                else:
                    self.get_libre_connection()
                    if self.cgm_err == '':
                        self.get_libre_bginfo()
                    if self.cgm_err =='':
                        self.current = 'sweetlight'
                    else:
                        self.current = 'login'

    def cgm_update_bg(self, dt):
        #if there is no data query server
        if self.current_bg == '-1':
            if self.cgm == 'dexcom':
                self.get_dex_bg()
            else:
                self.get_libre_bginfo()
        #or it's been longer than 5.1 mins query server
        else:
            self.mins_since_last_reading = (datetime.now() - self.last_reading).total_seconds() / 60.0
            if self.mins_since_last_reading > 5.1:
                if self.cgm == 'dexcom':
                    self.get_dex_bg()
                else:
                    self.get_libre_bginfo()

    def get_dex_bg(self):
        if self.location == 'US':
            residence = False
        else:
            residence = True
        try:
            bg_list = Dexcom(self.username,self.password, residence).get_glucose_readings(minutes=16)
        except Exception as e:
            self.cgm_err =repr(e)
            self.current_bg = '-1'
        else:
            if not bg_list:
                self.current_bg = '-1'
            else:
                self.cgm_err = ''
                self.current_bg = str(bg_list[0].value)
                self.last_reading = bg_list[0].time
                if bg_list[0].trend_arrow != '?':
                    self.trend_arr = bg_list[0].trend_arrow
                else:
                    self.trend_arr = ''
                self.mins_since_last_reading = (datetime.now() - self.last_reading).total_seconds() / 60.0
                if self.mins_since_last_reading > 15.5:
                    self.current_bg = '-1'

    def get_libre_connection(self):
        try:
            libre = Libre(self.username, self.password, self.location)
        except Exception as e:
            self.cgm_err =repr(e)
            self.current_bg = '-1'
        else:
            self.libreconnection = libre
            self.cgm_err = ''

    def get_libre_bginfo(self):
        try:
            (self.current_bg,self.last_reading,self.trend_arr) = self.libreconnection.get_libre_latest()
        except Exception as e:
            self.cgm_err =repr(e)
            self.current_bg = '-1'
        else:
            if not self.last_reading:
                self.current_bg == '-1'
            else:
                self.mins_since_last_reading = (datetime.now() - self.last_reading).total_seconds() / 60.0
                if self.mins_since_last_reading > 15.5:
                    self.current_bg = '-1'
            self.cgm_err = ''

        #this will need to update colors
    def on_current_bg(self, instance, value):
        #if there is no data, turn it black/off, otherwise update the color AND last reading is older than 16mins or there is no last reading
        if self.current_bg == '-1' and ((self.mins_since_last_reading > 15.2) or (self.mins_since_last_reading == 0)):
            self.label_color = [0,0,0,1]
            self.red = 0
            self.green = 0
            self.blue = 0
            #here's the problem
            #self.cgm_err = 'No Data'

            if not self.bulb_obj:
                self.bulb_err = ''
            # else try to connect to bulb and then turn it off since there's no data
            elif bulb != '-1':
                try:
                    self.bulb_obj.turn_off()
                except Exception as e:
                    self.bulb_err = repr(e)
                else:
                    self.bulb_err = ''
        else:
            #set label color
            self.rgb(int(value))
            self.current_bg_mmol = str(round((int(self.current_bg) *  0.0555555555555556),1))
            #set bulb color
            if not self.bulb_obj or (self.bulb == '-1'):
                self.bulb_err = ''
            else:
                try:
                    #if bulb was ever turned off b/c of no data
                    self.bulb_obj.turn_on()
                    self.bulb_obj.set_rgb(round(self.red), round(self.green), round(self.blue))
                except Exception as e:
                    self.bulb_err = repr(e)
                else:
                    self.bulb_err = ''
                    #we could insert a fn here that strips out some of the bad range of values for a strip light

    def rgb(self, bg):
        self.bg_to_red(bg)
        self.bg_to_green(bg)
        self.bg_to_blue(bg)

    def bg_to_red(self, bg):
        #bg's < normal are blues and greens and have no red
        if bg <= self.normal:
            red = 0
        else:
            red = ((bg - self.normal) / (self.elevated - self.normal)) * 255
            if red > self.color_max:
                red = self.color_max
        self.red = red
        self.label_color[0] = red / 255.0

    def bg_to_green(self, bg):
        if bg <= self.urgent:
            green = 0
        elif bg <= self.elevated:
            green = ((bg - self.urgent) / (self.low - self.urgent)) * 255
            if green > self.color_max:
                green = self.color_max
        else:
            green = 255 - (((bg - self.elevated) / (self.high - self.elevated)) * 255)
            if green < self.color_min:
                green = self.color_min
        self.green = green
        self.label_color[1] = green / 255.0

    def bg_to_blue(self, bg):
            if bg <= self.low:
                blue = 255
            elif bg <= self.high:
                blue = 255 - (((bg - self.low) / (self.normal - self.low)) * 255)
                if blue < self.color_min:
                    blue = self.color_min
            else:
                blue = (((bg - self.high) / (self.super_high - self.high)) * 255)
                if blue > self.color_max:
                    blue = self.color_max
            self.blue = blue
            self.label_color[2] = blue / 255.0

class Spec(App):
    title = 'Spectrum CGM'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_exists = False
        self.me = singleton.SingleInstance()

    def build(self):
        try:
            ini = self.get_application_config()
            self.config.read(ini)
            self.config.get('user', 'username')
        except configparser.NoSectionError:
            self.user_exists = False
        else:
            self.user_exists = True
        return Spectrum()


if __name__ == '__main__':
    Spec().run()