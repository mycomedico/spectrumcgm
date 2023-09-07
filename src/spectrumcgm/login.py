# File name: login.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty
from plyer import keystore


class MyPopup(Popup):
    pass


class Login(Screen):
    cgm = StringProperty('')
    location = StringProperty('')
    loading = NumericProperty(1)
    cgm_note = StringProperty('')

    def on_enter(self):
        #currently this will always run update for multi-user version
        app = App.get_running_app()
        if not app.user_exists:
            popup = MyPopup()
            popup.open()

    def on_cgm(self,instance,value):
        if value == 'dexcom':
            self.cgm_note = 'Enable Dexcom Share service (follow app).'
        elif value == 'libre':
            self.cgm_note = 'Use LibreLinkUp login credentials.'
        else:
            self.cgm_note = ''

    # need to accept email and determine if its dexcom or libre for now just accepts dexcom
    def do_login(self, logintext, passwordtext):
        self.manager.cgm = self.cgm
        self.manager.location = self.location
        self.manager.username = logintext
        self.manager.password = passwordtext

        if self.cgm == 'dexcom':
            self.manager.get_dex_bg()
            if self.manager.cgm_err == '':
                # create settings file
                app = App.get_running_app()
                app.config.read(app.get_application_config())
                app.config.adddefaultsection('user')
                app.config.setall('user', {'username': logintext, 'cgm': self.cgm, 'location': self.location})
                try:
                    keystore.set_key('spectrumcgm', logintext, passwordtext)
                except:
                    pass
                else:
                    app.config.write()
                self.manager.current = 'lightconfig'
            else:
                self.loading = 1
                self.ids._login_but.disabled = False

        else:
            self.manager.get_libre_connection()
            if self.manager.cgm_err == '':

                    self.manager.get_libre_bginfo()

                    if self.manager.cgm_err == '':
                        app = App.get_running_app()
                        app.config.read(app.get_application_config())
                        app.config.adddefaultsection('user')
                        app.config.setall('user', {'username': logintext, 'cgm': self.cgm, 'location': self.location})
                        try:
                            keystore.set_key('spectrumcgm', logintext, passwordtext)
                        except:
                            pass
                        else:
                            app.config.write()

                        self.loading = 1
                        self.ids._login_but.disabled = False
                        # switch to the light config screen
                        self.manager.current = 'lightconfig'
                    else:
                        self.loading = 1
                        self.ids._login_but.disabled = False
            else:
                self.loading = 1
                self.ids._login_but.disabled = False
