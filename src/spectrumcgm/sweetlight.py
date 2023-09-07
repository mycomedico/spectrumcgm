# filename: sweetlight.py


from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class SweetLight(Screen):

    # clock functions
    def on_enter(self):
        self.check_bg = Clock.schedule_interval(self.manager.cgm_update_bg, 30)

    def on_leave(self):
        self.check_bg.cancel()
