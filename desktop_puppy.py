
# pip install PyQt5

'''
1. Automatic state switching based on computer time: 

23:00-12:00 → sleep
12:00-19:00 → study
19:00-20:00 → guitar
20:00-23:00 → game
Otherwise → idle


2. Right-click context menu features:

Supports manual state switching (study, guitar, game, sleep, idle)
Allows using "Say something…" to add or modify a speech bubble (up to 10 characters)
Provides an option to display the current status (mood, energy, and a message)
Supports clearing the speech bubble
Includes a reset function (allowed only once per day)
Contains a quit option to exit the application


3. ood and energy system:

Both mood and energy values range from 0 to 5
Automatically adjusts mood and energy when entering a state
Prevents state switching if mood or energy is too low (e.g., below 2), showing a warning
Forces the pet to switch to idle if mood is 1
Forces switch to sleep if energy is 1


4. Click interaction system:

Left-click dragging moves the desktop pet window
Double-clicking (simulated petting) accumulates clicks When a random threshold is reached, 
the pet's mood increases by 1 (up to a maximum of 5)
and a heart animation is triggered There is a 1-minute cooldown after a successful petting action
'''




import sys                                      # Import system modules
import random                                   # Import a random module to generate random numbers
import time                                     # Import time module for recording time
import os                                       # Import the operating system module and process the file path
from datetime import datetime, date             # Import date and time classes
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation  # Import core modules (timer, animation, etc.)
from PyQt5.QtGui import QMovie, QPixmap, QCursor   # Import graphics module (gif animation, pictures, cursor)
from PyQt5.QtWidgets import (                     # Import widgets
    QApplication, QLabel, QMainWindow, QMenu, QAction,
    QInputDialog, QMessageBox, QGraphicsOpacityEffect
)

# Define the desktop pet main window class, inherited from QMainWindow
class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()  # Initialize the parent class
        
        # Define the main window pixel size (150 pixels in width and height)
        self.window_size = 150
        
        # Define the target size of the love animation (the original image is 360×360, which will be scaled to the specified size to display)
        self.heart_target_size = 60
        
        # Set reset reset chances that are only allowed once a day
        self.reset_chance = 1
        self.last_reset_date = date.today()  # Record the date of the last reset
        
        # Record the last successful time to increase mood by double-clicking (used to increase mood by 1 minute cooling when double-clicking)
        self.last_successful_double_click = 0
        
        # Get the desktop available area and position the window in the lower right corner, but leave 20 pixels on the right without sticking it
        screen_geometry = QApplication.desktop().availableGeometry()  # Get the screen available area (exclude taskbar)
        x = screen_geometry.width() - self.window_size - 20         # Calculate x coordinates: Leave 20px on the right
        y = screen_geometry.height() - self.window_size                # Calculate y coordinates
        self.move(x, y)         # Move the window to the specified location
        
        # Initialize pet status variables: Set the initial state according to the current time, and set the mood and physical strength values ​​at the same time.
        self.status = self.get_time_based_status()  # Initial state (study, sleep, guitar, game, idle)
        self.mood = 5          # Set the initial mood value to 5 (the range is 0~5, and it will automatically enter the idle state when it is 0)
        self.energy = 5        # Set the initial physical strength value to 5 (the range is 0~5, and it will automatically enter the sleep state when it is 0)
        self.last_sleep_time = None  # Used to record the start time of a pet entering sleep state
        
        # Initialize double-click to touch related variables
        self.pet_touch_count = 0                                # Cumulative number of double-click strokes
        self.double_click_threshold = random.randint(3, 8)        # Randomly generated trigger to increase mood by double-clicking (3 to 8 times)
        self.last_double_click_time = 0                          # Record the last double-click time
        
        self.bubble_label = None     # Tags used to display the "Say something" input bubble
        
        # Set window properties: no border, always topped, transparent background and displayed as a separate window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize the main tag (used to display gif animations), allowing content to automatically scale
        self.label = QLabel(self)
        self.label.setScaledContents(True)  # Allows automatic scaling of tag content
        self.setCentralWidget(self.label)   # Set label as the center component of the window
        self.setFixedSize(self.window_size, self.window_size)  # Fixed window size
        
        self.show()            # Display window
        self.repaint
        self.raise_()          # Place the window on top
        self.activateWindow()  # Activate the window to gain focus
        
        # Load the gif animation corresponding to the current state
        self.label.clear()
        self.label.setStyleSheet("background: transparent;")
        self.update_gif()
        
        # Set the right-click menu: Call the open_menu() method when right-clicking
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)
        
        # Setting up mouse events:
        # Bind the left-click event to self.label, to increase mood
        self.label.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        # At the same time, the drag window function is implemented, and it is implemented by rewriting mousePressEvent and mouseMoveEvent
        
        # Print window initialization debug information to terminal
        print('Window initialization completed')
        print("Window geometry:", self.geometry())
        print("Is window visible:", self.isVisible())
        print("Window size:", self.size())

    # Return to the initial state according to the current time
    def get_time_based_status(self):
        now = datetime.now().hour  # Get the current hour
        if 23 <= now or now < 12:
            return "sleep"       # Sleep state from 23:00 to 11:59
        elif 12 <= now < 19:
            return "study"       # 12:00 to 18:59 in study status
        elif 19 <= now < 20:
            return "guitar"      # 19:00 to 19:59 in guitar status
        elif 20 <= now < 23:
            return "game"        # 20:00 to 22:59 in game state
        return "idle"            # The default time is idle status

    # Return the corresponding gif file path according to the current status and mood
    def get_gif_path(self):
        base = os.path.dirname(__file__)  # Get the directory where the current file is located
        if self.status == "study":
            return os.path.join(base, "assets", f"study_{self.get_mood_suffix()}.gif")
        elif self.status == "game":
            return os.path.join(base, "assets", f"game_{self.get_mood_suffix()}.gif")
        elif self.status == "guitar":
            return os.path.join(base, "assets", "guitar.gif")
        elif self.status == "sleep":
            return os.path.join(base, "assets", "sleep.gif")
        elif self.status == "idle":
            return os.path.join(base, "assets", "idle.gif")
        else:
            return os.path.join(base, "assets", "idle.gif")

    # Select the suffix based on the current mood value, which is used to select the correct GIF group (bad, normal, happy)
    def get_mood_suffix(self):
        if self.mood <= 1:
            return "bad"
        elif self.mood >= 5:
            return "happy"
        else:
            return "normal"

    # The modified update gif() function is used to load and display gifs to prevent residual problems in the first frame.
    def update_gif(self):
        path = self.get_gif_path()  # Get the path to the GIF file that should be displayed currently
        # If an old movie object exists, stop the animation and clear the contents of the label
        if hasattr(self, "movie") and self.movie:
            self.movie.stop()
            self.label.clear()
        self.current_gif_path = path  # Save the current gif path
        self.movie = QMovie(path)      # Create a new q movie instance to load gif
        if not self.movie.isValid():
            return  # Exit if loading fails
        # Start the animation and force it to return to the first frame to avoid residual phenomena
        self.movie.start()
        self.movie.jumpToFrame(0)
        self.label.setMovie(self.movie)  # Set the new animation to the tag
        self.movie.setSpeed(100)           # Set animation playback speed

    # State switching method, adjust mood and physical strength according to the target state, and update animation display at the same time
    def set_status(self, new_status):
        # If the target state is consistent with the current state, only prompt information is displayed
        if new_status == self.status:
            state_messages = {
                "study": "You are studying now!",
                "guitar": "Immersing in music...",
                "game": "Don't play too much game!",
                "sleep": "Already Zzz",
                "idle": "Do something..."
            }
            msg = state_messages.get(new_status, "")
            self.show_state_tip(msg)  # Show prompts in the window
            print(msg)
            return

        # If you are currently in sleep and switch to other states, you will restore your mood and physical strength based on the length of sleep.
        if self.status == "sleep" and new_status != "sleep" and self.last_sleep_time:
            sleep_duration = time.time() - self.last_sleep_time
            if sleep_duration >= 3600:
                self.energy = 5
                self.mood = min(5, self.mood + 2)
            else:
                self.energy = min(5, self.energy + 2)
            self.last_sleep_time = None

        # For switching to study state, the mood and physical strength are required to be at least 2, otherwise the prompt will fail.
        if new_status == "study":
            if self.mood < 2:
                self.show_warning("Don't have enough mood")
                print("Don't have enough mood")
                return
            if self.energy < 2:
                self.show_warning("Don't have enough energy")
                print("Don't have enough energy")
                return
            self.mood = max(0, self.mood - 2)
            self.energy = max(0, self.energy - 1)
        elif new_status == "guitar":
            if self.energy == 0:
                self.show_warning("Energy too low!")
                print("Energy too low!")
                return
            self.mood = min(5, self.mood + 1)
            self.energy = max(0, self.energy - 1)
        elif new_status == "game":
            if self.energy == 0:
                self.show_warning("Energy too low!")
                print("Energy too low!")
                return
            self.mood = min(5, self.mood + 2)
        elif new_status == "sleep":
            if not self.last_sleep_time:
                self.last_sleep_time = time.time()
        elif new_status == "idle":
            # Increase 1 point of physical strength when switching to idle state
            self.energy = min(5, self.energy + 1)

        # Automatic rules: If the mood drops to 0, it will automatically enter idle; if the physical strength drops to 0, it will automatically enter sleep
        if self.mood == 0:
            self.status = "idle"
        elif self.energy == 0:
            self.status = "sleep"
            if not self.last_sleep_time:
                self.last_sleep_time = time.time()
        else:
            self.status = new_status
        
        print(f"Switched to {self.status}. ")
        self.print_status_message()   # Output current status information to the terminal
        self.update_gif()             # Update gif animation display

    # Output current status information (mood, physical strength and prompts) to the terminal
    def print_status_message(self):
        mood_suffix = self.get_mood_suffix()
        if mood_suffix == "happy":
            status_msg = "Your puppy is happy now ｡:ﾟ૮ ˶ˆ ﻌ ˆ˶ ა ﾟ:｡"
        elif mood_suffix == "normal":
            status_msg = "Your puppy is at a good mood ૮ ˶′ﻌ ‵˶ ა"
        else:
            status_msg = "Please pet your puppy ૮ ◞ ﻌ ◟ ა"
        print(f"Mood: {self.mood}, Energy: {self.energy}. {status_msg}")

    # Show warning labels (black text), such as "under energy" or "under mood"
    def show_warning(self, message):
        warn_label = QLabel(message, self)
        warn_label.setStyleSheet("color: black; font-size: 16px; background-color: rgba(255,255,255,0.7);")
        warn_label.setWordWrap(True)
        warn_label.adjustSize()
        # Place the warning label in the center of the window
        warn_label.move((self.width() - warn_label.width()) // 2,
                        (self.height() - warn_label.height()) // 2)
        warn_label.show()
        QTimer.singleShot(2000, warn_label.deleteLater)  # Automatically deleted after 2 seconds

    # When the request switches to the same as the current state, the corresponding prompt information is displayed
    def show_state_tip(self, message):
        tip_label = QLabel(message, self)
        tip_label.setStyleSheet("color: black; font-size: 16px; background-color: rgba(255,255,255,0.7);")
        tip_label.setWordWrap(True)
        tip_label.adjustSize()
        tip_label.move((self.width() - tip_label.width()) // 2,
                       (self.height() - tip_label.height()) // 2)
        tip_label.show()
        QTimer.singleShot(2000, tip_label.deleteLater)

    # Right-click menu, including: Change Status, Say something..., Show Status, Clear bubble, Reset, Quit
    # Menu arrangement requires Reset to be above Quit (the second to last item)
    def open_menu(self, pos):
        menu = QMenu()
        
        # Add Change Status submenu
        change_status_menu = menu.addMenu("Change Status")
        for state in ["study", "guitar", "game", "sleep", "idle"]:
            action = QAction(state.capitalize(), self)
            action.triggered.connect(lambda checked, s=state: self.set_status(s))
            change_status_menu.addAction(action)
        
        # Add Say something... option
        bubble_action = QAction("Say something...", self)
        bubble_action.triggered.connect(self.show_bubble_input)
        menu.addAction(bubble_action)
        
        # Add Show Status option
        show_status_action = QAction("Show Status", self)
        show_status_action.triggered.connect(self.show_status_window)
        menu.addAction(show_status_action)
        
        # Add Clear bubble option
        clear_bubble = QAction("Clear bubble", self)
        clear_bubble.triggered.connect(self.clear_bubble)
        menu.addAction(clear_bubble)
        
        # Add Reset option (the second to last item)
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_status)
        menu.addAction(reset_action)
        
        # Add Quit option (bottom)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)
        
        menu.exec_(QCursor.pos())  # Display menu in the current mouse position

    # Display the "Say something..." input box
    def show_bubble_input(self):
        text, ok = QInputDialog.getText(self, "Talk", "Enter something (max 10 chars):")
        if ok and text.strip():
            self.show_bubble(text[:10])
    
    # Display input bubbles in the top window directly below the table pet, supporting automatic line wrapping
    def show_bubble(self, text):
        if self.bubble_label:
            self.bubble_label.close()
        self.bubble_label = QLabel(text)
        self.bubble_label.setStyleSheet("background-color: white; border: 1px solid gray; padding: 4px;")
        self.bubble_label.setWordWrap(True)
        self.bubble_label.adjustSize()
        pet_global = self.mapToGlobal(self.rect().bottomLeft())
        bubble_x = pet_global.x() + (self.width() - self.bubble_label.width()) // 2
        bubble_y = pet_global.y()
        self.bubble_label.move(bubble_x, bubble_y)
        self.bubble_label.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.bubble_label.show()
    
    # Clear input bubble display
    def clear_bubble(self):
        if self.bubble_label:
            self.bubble_label.close()
            self.bubble_label = None

    # Display the status window to display the current mood, physical strength and status prompts in the form of a dialog box
    def show_status_window(self):
        mood_suffix = self.get_mood_suffix()
        if mood_suffix == "happy":
            status_line = "Your puppy is happy now\n    ｡:ﾟ૮ ˶ˆ ﻌ ˆ˶ ა ﾟ:｡"
        elif mood_suffix == "normal":
            status_line = "Your puppy is at a good mood\n    ૮ ˶′ﻌ ‵˶ ა"
        else:
            status_line = "Please pet your puppy\n    ૮ ◞ ﻌ ◟ ա"
        text = f"Mood: {self.mood}\nEnergy: {self.energy}\n{status_line}"
        QMessageBox.information(self, "Status", text)
    
    # Reset function: Only once a day, please reset your mood and physical strength after asking the user, and re-judgment the status based on the current time.
    def reset_status(self):
        today = date.today()
        if today != self.last_reset_date:
            self.reset_chance = 1
            self.last_reset_date = today
        prompt = f"Do you want to reset all status?\nToday's reset chance: {self.reset_chance}/1"
        reply = QMessageBox.question(self, "Reset", prompt, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.reset_chance > 0:
                self.mood = 5
                self.energy = 5
                self.status = self.get_time_based_status()  # Re-judgment of the status based on the current time
                self.reset_chance -= 1  # Use a reset chance
                print("Reset successfully! Full mood and energy now!")
                QMessageBox.information(self, "Reset", "Reset successfully!")
                self.print_status_message()
                self.update_gif()
            else:
                print("No chance to reset... Just enjoy your day!")
                QMessageBox.information(self, "Reset", "No chance to reset... Just enjoy your day!")
        else:
            pass  # The user chooses not to reset and does not perform any operations

    # Drag and move pet function: rewrite the mouse press event, record the offset position relative to the upper left corner of the window when the left mouse button is clicked
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    # Drag and move pet function: rewrite mouse move event, update window position according to the current mouse global position
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    # Left-click event: used to increase mood and perform 1 minute cooling judgment at the same time
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            # If the last time I successfully increase my mood is less than 1 minute away from the current time, the prompt message will be displayed and exited
            if current_time - self.last_successful_double_click < 60:
                self.show_state_tip("The fur is getting bald!\ny—̳͟͞͞♥ ૮ ○ﻌ ○ ա")
                print("Wait a little bit before petting the puppy again—̳͟͞͞♥ ૮ ○ﻌ ○ ա")
                return
            # If the interval between two double-clicks exceeds 10 minutes, reset the cumulative double-click times and the random threshold.
            if current_time - self.last_double_click_time > 10 * 60:
                self.pet_touch_count = 0
                self.double_click_threshold = random.randint(3, 8)
            self.pet_touch_count += 1  # Cumulative number of double-clicks
            self.last_double_click_time = current_time
            print("Double click count:", self.pet_touch_count, "Threshold:", self.double_click_threshold)
            # If the cumulative number of double-clicks has reached the randomly set threshold, increase your mood
            if self.pet_touch_count >= self.double_click_threshold:
                self.mood = min(5, self.mood + 1)  # Increase mood, but no more than 5
                print("Pet touched! Mood increased to:", self.mood)
                self.last_successful_double_click = current_time  # Update the last time to increase mood time
                self.show_heart()                # Show love animation
                self.pet_touch_count = 0         # Reset the cumulative number of double-clicks
                self.double_click_threshold = random.randint(3, 8)  # Regenerate random double-click threshold
                self.print_status_message()      # Output the current status to the terminal
                self.update_gif()                # Update gif animation (reflects possible changes in state)

    # Show love animation:
    # Create a tag to load the love picture, scale it to the set size, make it appear in the middle, and fade out with a gradient animation, the animation duration is 3000 milliseconds
    # Show love animation (in the middle of the window, automatically fades)
    def show_heart(self):
        heart = QLabel(self)
        heart.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Loading love pictures
        heart_path = os.path.join(os.path.dirname(__file__), "assets/heart.png")
        pixmap = QPixmap(heart_path) 
        pixmap = pixmap.scaled(self.heart_target_size, self.heart_target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        heart.setPixmap(pixmap)

        # Use the true width and height of pixmap to center
        pixmap_size = pixmap.size()
        x = (self.width() - pixmap_size.width()) // 2
        y = (self.height() - pixmap_size.height()) // 2
        heart.setGeometry(x, y, pixmap_size.width(), pixmap_size.height())
        heart.setStyleSheet("background: transparent;")
        heart.show()

        # Add fade animation
        effect = QGraphicsOpacityEffect(heart)
        heart.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(3000)  # Animation time 3 seconds
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.finished.connect(heart.deleteLater)
        animation.start(QPropertyAnimation.DeleteWhenStopped)


# Program portal: Create an application and start the main event loop
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())
