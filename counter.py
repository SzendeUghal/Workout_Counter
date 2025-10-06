from kivy.app import App
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
#from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
import time



class CounterRun(FloatLayout):
    """
    Main widget for the counter app. Handles UI elements, logic, and state.
    """
    
    # Number of completed repetitions
    teljesitett = NumericProperty(0)
    # Target value to reach
    celertek = NumericProperty(0)
    # State flags
    stopper_runs_bool = False  # Is the stopwatch running?
    cel_elerve_bool = False    # Has the goal been reached?
    cel_beallitva_bool = False # Has the goal been set?
    # Stopwatch start time
    start_time = 0

    def __init__ (self, **kwargs):
        super(CounterRun , self).__init__(**kwargs)
        self.teljesitett = 0    
        self.celertek = 0

        # Add background image
        self.add_widget(Image(source="back_shot.jpg", allow_stretch=True, keep_ratio=True), index=0)
        
        # Labels for goal, completed count, and stopwatch
        self.cel_lbl = Label(text="[color=278cd4][b]Mit és mennyit?[/b][/color]", font_size= 20, size_hint=(0.4,0.1), pos_hint={"x":0.1, "y":0.7}, markup=True)
        self.add_widget(self.cel_lbl)

        self.teljesitett_lbl = Label(text="[color=278cd4][b]Teljesített: 0[/b][/color]", font_size=20, size_hint=(0.4,0.1), pos_hint={"x":0.1, "y":0.5}, markup=True)
        self.add_widget(self.teljesitett_lbl)

        self.stopper_lbl = Label(text="[color=278cd4][b]idomeres[/b][/color]", font_size=20, size_hint=(0.4,0.1), pos_hint={"x":0.1, "y":0.6}, markup=True)
        self.add_widget(self.stopper_lbl)

        # Text input for goal value
        self.cel_ertek = TextInput(text="Mennyi?", size_hint=(.25,.1), pos_hint={"x": .1, "y":0.85}, multiline=False)
        self.add_widget(self.cel_ertek)

        # Dropdown menu for exercise type
        self.edzesforma = DropDown()   
        for forma in ["Burpee", "Húzódzkodás", "Fekvőtámasz", "Guggolás", "Dip"]:
            btn = Button(text=forma, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn: self.edzesforma.select(btn.text))
            self.edzesforma.add_widget(btn)
        self.mainbutton = Button(text="Mit csinálsz?", size_hint=(.25,.1), pos_hint={"x": 0.4, "y": 0.85})
        self.mainbutton.bind(on_release=lambda btn: self.edzesforma.open(btn))
        self.edzesforma.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.add_widget(self.mainbutton)

        # Counter buttons (+1, +5, +10)
        self.plusz1_gomb = Button(text='+1', size_hint=(.25,.1), pos_hint={'x':0.1, 'y':0.3})
        self.plusz1_gomb.bind(on_press=lambda x: self.plusz1())
        self.plusz1_gomb.disabled = True
        self.add_widget(self.plusz1_gomb)

        self.plusz5_gomb = Button(text='+5', size_hint=(.25,.1), pos_hint={'x':0.4, 'y':0.3})
        self.plusz5_gomb.bind(on_press=lambda x: self.plusz5())
        self.plusz5_gomb.disabled = True
        self.add_widget(self.plusz5_gomb)

        self.plusz10_gomb = Button(text='+10', size_hint=(.25,.1), pos_hint={'x':0.7, 'y':0.3})
        self.plusz10_gomb.bind(on_press=lambda x: self.plusz10())
        self.plusz10_gomb.disabled = True
        self.add_widget(self.plusz10_gomb)

        # Button to set the goal
        self.ennyit_ezt_gomb = Button(text="cél megadása", size_hint=(.25,.1), pos_hint={"x": 0.7, "y": 0.85})
        self.ennyit_ezt_gomb.bind(on_press=lambda x: self.ennyit_ezt())
        self.add_widget(self.ennyit_ezt_gomb)

        # Start/stop/pause/quit buttons
        self.start_gomb = Button(text="Start", size_hint=(.35, 0.1), pos_hint={"x": .1, "y":0.15})
        self.start_gomb.bind(on_press=lambda x: self.stopper())
        self.add_widget(self.start_gomb)

        self.stop_gomb = Button(text="Stop/Pause", size_hint=(.35, 0.1), pos_hint={"x": .6, "y":0.15})
        self.stop_gomb.bind(on_press=lambda x: self.stopper_pause())
        self.add_widget(self.stop_gomb)

        self.quit_gomb = Button(text="Quit", size_hint=(.85, 0.1), pos_hint={"x": .1, "y":0.0})
        self.quit_gomb.bind(on_press=lambda x: self.quit())
        self.quit_gomb.background_color = (0.95, 0.2, 0.2, 1)  # Red color
        self.add_widget(self.quit_gomb)

    def ennyit_ezt(self):
        """
        Set the goal value and enable counter buttons. Only works if stopwatch is not running and goal is not already set.
        """
        if self.stopper_runs_bool == False and self.cel_beallitva_bool == False:
            try:    
                self.celertek = int(self.cel_ertek.text)
                self.teljesitett = 0
            except ValueError:
                return
            self.cel_lbl.text = f"[color=278cd4][b]Cél: {self.celertek}db {self.mainbutton.text}[/b][/color]"
            self.teljesitett_lbl.text = f"[color=278cd4][b]Teljesített:\n {self.teljesitett}[/b][/color]"
            self.cel_beallitva_bool = True
            self.plusz1_gomb.disabled = False
            self.plusz5_gomb.disabled = False
            self.plusz10_gomb.disabled = False
        else:
            return

    def cel_elerve(self):
        """
        Called after each increment. Checks if the goal is reached, stops the stopwatch, and updates the label.
        """
        if self.teljesitett >= self.celertek:
            self.teljesitett_lbl.text = f"[color=278cd4][b]Cél elérve! \n {self.teljesitett}[/b][/color]"
            Clock.unschedule(self.update_stopper)
            self.stopper_runs_bool = False
            self.cel_elerve_bool = True

    def plusz1(self):
        """
        Increment by 1 if allowed, update label, and check for goal.
        """
        if self.cel_beallitva_bool == True and self.cel_elerve_bool == False and self.stopper_runs_bool == True:
            self.teljesitett += 1 
            self.teljesitett_lbl.text = f"[color=278cd4][b]Teljesített:\n {self.teljesitett}[/b][/color]"
            self.cel_elerve()
        else:
            return

    def plusz5(self):
        """
        Increment by 5 if allowed, update label, and check for goal.
        """
        if self.cel_beallitva_bool == True and self.cel_elerve_bool == False and self.stopper_runs_bool == True:
            self.teljesitett += 5 
            self.teljesitett_lbl.text = f"[color=278cd4][b]Teljesített:\n {self.teljesitett}[/b][/color]"
            self.cel_elerve()
        else:
            return

    def plusz10(self):
        """
        Increment by 10 if allowed, update label, and check for goal.
        """
        if self.cel_beallitva_bool == True and self.cel_elerve_bool == False and self.stopper_runs_bool == True:
            self.teljesitett += 10 
            self.teljesitett_lbl.text = f"[color=278cd4][b]Teljesített:\n {self.teljesitett}[/b][/color]"
            self.cel_elerve()
        else:
            return


    def update_stopper(self, dt):
        """
        Update the stopwatch label with elapsed time. Called by Kivy Clock.
        """
        if self.start_time > 0:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            miliseconds = int((elapsed_time - int(elapsed_time)) * 100)
            self.stopper_lbl.text = f"[color=278cd4][b]{minutes:02}:{seconds:02}:{miliseconds:02}[/b][/color]"
        else:
            return

    def stopper(self):
        """
        Start the stopwatch if goal is set and not already running or reached.
        """
       # if self.teljesitett == 0 and self.celertek > 0:
        if self.stopper_runs_bool == False and self.cel_elerve_bool == False and self.cel_beallitva_bool == True:

            self.stopper_runs_bool = True
            self.start_time = time.time()
            Clock.schedule_interval(self.update_stopper, 1/60)

        else:
            return
    
    def stopper_pause(self):
        """
        Pause or resume the stopwatch depending on current state.
        """
        if self.stopper_runs_bool == True:
            self.stopper_runs_bool = False
            Clock.unschedule(self.update_stopper)
        elif self.cel_elerve_bool == True and self.stopper_runs_bool == False:
            return
        else:
            self.stopper_runs_bool = True
            #self.start_time = time.time()
            Clock.schedule_interval(self.update_stopper, 1/60)


    def quit(self):
        """
        Quit the application.
        """
        App.get_running_app().stop()
        pass

class CounterApp(App):
    """
    Main Kivy App class. Builds the CounterRun widget.
    """
    def build(self):
        counter = CounterRun()
        Window.clearcolor = ("7d9d9dff")
        #counter.ask_goal()
        #Clock.schedule_interval(counter.update, 1.0/60.0)
        return counter

if __name__ == '__main__':
    CounterApp().run()
