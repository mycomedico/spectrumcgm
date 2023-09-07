# File name: lightconfig.py
from kivy.app import App
from kivy.uix.screenmanager import Screen
from yeelight import discover_bulbs, Bulb
from kivy.properties import NumericProperty
from kivy.uix.button import Button
from kivy.metrics import dp

class LightConfig(Screen):

    loading = NumericProperty(1)

    def list_bulbs(self):
        self.ids.stack.clear_widgets()

        try:
            bulb_list = discover_bulbs()
        except Exception as e:
            self.manager.bulb_err = repr(e)
            self.manager.bulb = '-1'
        else:
            if not bulb_list:
                self.manager.bulb_err = ''
                self.manager.bulb = '-1'
            else:
                #clear out any  error messages b/c fn just ran successfully
                self.manager.bulb_err = ''

                for i in range(len(bulb_list)):
                    #if bulb_list[i]['capabilities']['color_mode'] == '1':
                    address = bulb_list[i]['ip']
                    model = bulb_list[i]['capabilities']['model']
                    btn = Button(text=f'Yeelight #{i + 1} \nIP: ' + address + '\nModel: ' + model, size_hint=(None, None), size = (dp(150),dp(70)))
                    btn.btn_ip = address
                    # https://stackoverflow.com/questions/69063217/how-to-get-id-of-the-button-pressed-in-kivy
                    btn.bind(on_press = self.select_bulb)
                    self.ids.stack.add_widget(btn)
        finally:
            self.loading = 1
            self.ids._detect.disabled = False

    def select_bulb(self, instance):

        try:
            self.manager.bulb_obj = Bulb(instance.btn_ip)
        except Exception as e:
            self.manager.bulb_err = repr(e)
            self.manager.bulb = '-1'
        else:
            self.manager.bulb_err = ''
            self.manager.bulb = instance.btn_ip
            self.manager.bulb_obj.turn_on()
            #see if this works
            #need something here to check if there are current bg and then update those colors to the bulb
            #say the user profile was loaded and there was no bulb loaded
            if self.manager.current_bg != '-1' or '':
                self.manager.bulb_obj.set_rgb(round(self.manager.red), round(self.manager.green), round(self.manager.blue))
            app = App.get_running_app()
            app.config.read(app.get_application_config())
            app.config.set('user', 'bulb', instance.btn_ip)
            app.config.write()
            self.manager.current = 'sweetlight'

    def desel_bulb(self):
        #self.manager.bulb_obj = None
        self.manager.bulb = '-1'
        self.manager.bulb_err = ''
        app = App.get_running_app()
        app.config.read(app.get_application_config())
        app.config.set('user', 'bulb', self.manager.bulb)
        app.config.write()
        self.manager.current = 'sweetlight'