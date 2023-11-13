# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 21:01:02 2023

@author: pizzacoin
"""

# %%

from model import UGG_Park
from model import UGG_Round
import controller
import validators
import wx

# %%

INPUT_ERROR_MSG = "Please correct your input values!"

# %%

def show_message(message, caption, flag=wx.ICON_ERROR):
    msg = wx.MessageDialog(None, message=message, caption=caption, style=flag)
    msg.ShowModal()
    msg.Destroy()
    
# %%


class CourseTeeDialog(wx.Dialog):
    def __init__(self, parent, course):
        super().__init__(parent)
        self.course = course
        self.session = parent.parent.session
        self.available_colors = controller.get_tee_colors(
            self.session, self.course.course_id)
        self.create_ui()

    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        colors = controller.get_tee_colors(self.session, self.course.course_id)
        self.color_cbo = wx.ComboBox(
            self, size=(100, -1), choices=[color[1] for color in colors])
        self.submit_button = wx.Button(self, label="Submit")
        self.submit_button.Bind(wx.EVT_BUTTON, self.on_submit_button)
        sizer.Add(self.add_widgets(sizer, "Tee Color", self.color_cbo))      
        sizer.Add(self.submit_button, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizerAndFit(sizer)
        self.Layout()
    
    def add_widgets(self, sizer, text, field):
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label=text, size=(100, -1))
        h_sizer.Add(title, 0, wx.ALL, 5)
        h_sizer.Add(field, 0, wx.ALL, 5)
        return h_sizer
    
    def on_submit_button(self, event):
        color = self.color_cbo.GetValue()
        controller.create_course_tees(self.session, self.course, color)
        self.Close()

# %%

class ParkDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = parent.parent.session
        self.privacy_types = controller.get_privacy_types(self.session)
        self.create_ui()
        
    def get_park_names(self):
        return controller.get_park_names(self.session)
        
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.input_park_name = wx.TextCtrl(
            self, value="", size=(200, -1),
            validator=validators.ParkNameValidator(self.get_park_names()))
        sizer.Add(self.add_widgets(sizer, 'Park Name', self.input_park_name))

        self.input_website = wx.TextCtrl(self, value="", size=(200, -1))
        sizer.Add(self.add_widgets(sizer, 'Website', self.input_website))
        
        self.input_privacy_type = wx.ComboBox(
            self, choices=[t[1] for t in self.privacy_types], size=(200, -1))
        sizer.Add(self.add_widgets(sizer, 'Privacy Type', self.input_privacy_type))
        
        self.button_submit = wx.Button(self, label="Create", size=(100, -1))
        sizer.Add(
            self.button_submit, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.button_submit.Bind(wx.EVT_BUTTON, self.on_submit_button)
        
        self.SetSizerAndFit(sizer)
        self.Layout()
    
    def add_widgets(self, sizer, text, field):
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label=text, size=(100, -1))
        h_sizer.Add(title, 0, wx.ALL, 5)
        h_sizer.Add(field, 0, wx.ALL, 5)
        return h_sizer

    def on_submit_button(self, event):
        if self.validate():
            self.save()
            self.Close()
        
    def save(self):
        park_name = self.input_park_name.GetValue()
        website = self.input_website.GetValue()
        privacy_type = self.input_privacy_type.GetValue()
        privacy_type_id = [
            r[0] for r in self.privacy_types
            if r[1] == privacy_type
        ][0]
        park = UGG_Park(self.session, privacy_type_id, park_name, website)
        park.save()
        
    def validate(self):
        validation_list = []
        valid = self.input_park_name.GetValidator().Validate(
            self.input_park_name)
        validation_list.append(valid)
        if all(validation_list):
            return True
        else:
            msg = wx.MessageDialog(
                None, message=INPUT_ERROR_MSG, 
                caption="Save Failure", style=wx.ICON_ERROR)
            msg.ShowModal()
            msg.Destroy()
            return False

# %% 

class CourseDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.session = parent.parent.session
        self.park_id = parent.park.park_id
        self.create_ui()
        
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.course_name = wx.TextCtrl(self, size=(200,-1))
        self.holes_cbo = wx.ComboBox(self, choices=['9', '18', '27'])
        self.enter_button = wx.Button(self, label="Submit")
        sizer.Add(self.add_widgets("Course Name", self.course_name))
        sizer.Add(self.add_widgets("Number of Holes", self.holes_cbo))
        sizer.Add(self.enter_button, 0, wx.CENTER|wx.BOTTOM, 5)
        self.enter_button.Bind(wx.EVT_BUTTON, self.on_submit_button)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def add_widgets(self, text, field):
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label=text, size=(100, -1))
        h_sizer.Add(title, 0, wx.ALL, 5)
        h_sizer.Add(field, 0, wx.ALL, 5)
        return h_sizer
    
    def on_submit_button(self, event):
        self.save()
        self.Close()
        
    def save(self):
        course_name = self.course_name.GetValue()
        no_of_holes = self.holes_cbo.GetValue()
        controller.create_course(
            self.session, self.park_id, course_name, no_of_holes)

# %%

class PlayerDialog(wx.Dialog):
    def __init__(self, parent, round_id):
        super().__init__(parent)
        self.parent = parent
        self.session = parent.session
        self.round_id = round_id
        self.players_added = 0
        self.set_number_of_players()
        self.set_golfers()
        self.create_ui()
        
    def get_all_golfers(self):
        return controller.get_golfers(self.session)
    
    def set_golfers(self):
        self.selected_player_ids = []
        if self.round_id:
            self.selected_player_ids = controller.get_player_ids(
                self.session, self.round_id)
        self.players_added = len(self.selected_player_ids)
    
    def set_number_of_players(self):
        self.number_of_players = controller.get_number_of_players(
            self.parent.session,
            self.round_id)
    
    def transfer_golfer(self, index, is_adding=True):
        from_object = self.cbo_available_players \
            if is_adding else self.cbo_selected_players
        to_object = self.cbo_selected_players \
            if is_adding else self.cbo_available_players
        golfer_id = from_object.GetItemText(index, 0)
        golfer_name = from_object.GetItemText(index, 1)
        to_object.Append([golfer_id, golfer_name])
        from_object.DeleteItem(index)
    
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_button = wx.Button(self, label="Add", size=(100, - 1))
        add_button.Bind(wx.EVT_BUTTON, self.on_add)
        remove_button = wx.Button(self, label="Remove", size=(100, -1))
        remove_button.Bind(wx.EVT_BUTTON, self.on_remove)
        h_sizer.Add(add_button, 0, wx.CENTER)
        h_sizer.Add(remove_button, 0, wx.CENTER)
        self.cbo_selected_players = wx.ListCtrl(
            self, size=(300, 105), style=wx.LC_REPORT)
        self.cbo_selected_players.InsertColumn(0, "GolferID")
        self.cbo_selected_players.InsertColumn(
            1, "Golfer Name", width=wx.LIST_AUTOSIZE_USEHEADER)
        self.cbo_available_players = wx.ListCtrl(
            self, size=(300, 350), style=wx.LC_REPORT)
        self.submit_button = wx.Button(self, label="Submit")
        self.submit_button.Bind(wx.EVT_BUTTON, self.on_submit)
        self.cbo_available_players.InsertColumn(0, "GolferID")
        self.cbo_available_players.InsertColumn(
            1, "Golfer Name", width=wx.LIST_AUTOSIZE_USEHEADER)
        for golfer in self.get_all_golfers():
            name, golfer_id = golfer
            if golfer_id not in self.selected_player_ids:
                self.cbo_available_players.Append([golfer_id, name])
            else:
                self.cbo_selected_players.Append([golfer_id, name])
        sizer.Add(self.cbo_selected_players, 0, wx.RIGHT|wx.LEFT|wx.TOP, 5)
        sizer.Add(h_sizer, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(self.cbo_available_players, 0, wx.RIGHT|wx.LEFT|wx.BOTTOM, 5)
        sizer.Add(self.submit_button, 0, wx.CENTER, 5)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def on_submit(self, event):
        selected_golfer_ids = []
        for index in range(self.cbo_selected_players.GetItemCount()):
            selected_golfer_ids.append(
                self.cbo_selected_players.GetItemText(index, 0))
        self.parent.data["golfer_ids"] = selected_golfer_ids
        self.Close()
    
    def on_remove(self, event):
        selected = []
        last_index = -1
        count_of_selected = self.cbo_selected_players.GetSelectedItemCount()
        if count_of_selected == 0:
            return
        for _ in range(count_of_selected):
            item_index = self.cbo_selected_players.GetNextSelected(last_index)
            last_index = item_index
            if item_index != -1:
                selected.append(item_index)
        for index in reversed(selected):
            self.players_added -= 1
            self.transfer_golfer(index, False)
    
    def on_add(self, event):
        selected = []
        last_index = -1
        count_of_selected = self.cbo_available_players.GetSelectedItemCount()
        if self.number_of_players < count_of_selected + self.players_added \
        or count_of_selected == 0:
            return
        for _ in range(count_of_selected):
            item_index = self.cbo_available_players.GetNextSelected(last_index)
            last_index = item_index
            if item_index != -1:
                selected.append(item_index)
        for index in reversed(selected):
            self.players_added += 1
            self.transfer_golfer(index, True)
            
            
# %%
    
class RoundDialog(wx.Dialog):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.parent = parent
        self.session = session
        self.course_list = controller.get_active_golf_courses(self.session)
        self.course_tee_list = []
        self.create_ui()
            
    def add_widgets(self, sizer, text, field):
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label=text, size=(150, -1))
        h_sizer.Add(title, 0, wx.ALL, 5)
        h_sizer.Add(field, 0, wx.ALL, 5)
        return h_sizer
        
    def get_courses(self):
        return [course[1] for course in self.course_list]
    
    def get_course_tees(self):
        return [tee[1] for tee in self.course_tee_list]
        
    def set_course_tees(self, event):
        self.course_tee_list = controller.get_course_tees(
            self.session, self.retrieve_course_id())
        self.cbo_course_tees.Clear()
        self.cbo_course_tees.Append(self.get_course_tees())
    
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        CBO_SIZE = (200, -1)
        player_choices = ['4 - Four', '3 - Three', '2 - Two', '1 - One']

        self.cbo_courses = wx.ComboBox(
            self, choices=self.get_courses(), size=CBO_SIZE,
            validator=validators.ComboBoxValidator(self.get_courses()))
        self.cbo_courses.Bind(wx.EVT_COMBOBOX, self.set_course_tees)
        sizer.Add(self.add_widgets(sizer, "Golf Course", self.cbo_courses))
        self.cbo_course_tees = wx.ComboBox(
            self, choices=self.get_course_tees(), size=CBO_SIZE,
            validator=validators.ComboBoxValidator(self.get_course_tees()))
        sizer.Add(self.add_widgets(sizer, "Course Tee Color", self.cbo_course_tees))
        self.cbo_players = wx.ComboBox(
            self, choices=player_choices, size=CBO_SIZE,
            validator=validators.ComboBoxValidator(player_choices))
        sizer.Add(self.add_widgets(
            sizer, "Number of Players", self.cbo_players))
        button = wx.Button(self, label="Submit", size=(100, -1))
        sizer.Add(button, 0, wx.BOTTOM|wx.CENTER, 5)
        button.Bind(wx.EVT_BUTTON, self.on_button_press)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def validate(self):
        validation_list = []
        for ctrl in [self.cbo_courses, self.cbo_players]:
            valid = ctrl.GetValidator().Validate(ctrl)
            validation_list.append(valid)
        validation_list.append(
            self.cbo_course_tees.GetValidator().Validate(
                self.cbo_course_tees, self.get_course_tees()))
        if all(validation_list):
            return True
        else:
            msg = wx.MessageDialog(
                None, message=INPUT_ERROR_MSG, 
                caption="Save Failure", style=wx.ICON_ERROR)
            msg.ShowModal()
            msg.Destroy()
            return False
        
    def retrieve_course_id(self):
        selected_course = self.cbo_courses.GetValue()
        return [course[0] for course in self.course_list 
                if course[1] == selected_course][0]
        
    def save(self):
        course_id = self.retrieve_course_id()
        no_of_players = self.cbo_players.GetValue()[0]
        new_round = UGG_Round(self.session, course_id, no_of_players)
        new_round.save()
        self.parent.data["round_id"] = new_round.RoundID
        
    def on_button_press(self, event):
        if self.validate():
            self.save()
            self.Close()

# %%
    
class ScoreDialog(wx.Dialog):
    def __init__(self, parent, data=None, 
                 num_of_holes=18, validator_type="par"):
        super().__init__(parent)
        self.validator_type = validator_type
        self.num_of_holes = num_of_holes
        self.parent = parent
        self.create_ui()
        if data:
            self.load_data(data)
            
    def get_validator(self):
        if self.validator_type == "par":
            validator = validators.ParValidator()
        elif self.validator_type == "distance":
            validator = validators.DistanceValidator()
        else:
            validator = None
        return validator
            
        
    def load_data(self, data):
        for prop, value in vars(self).items():
            if "input_" in prop:
                attr = getattr(self, prop)
                number = int(prop[-2:])
                if not data[number]:
                    new_value = ""
                else:
                    new_value = str(data[number])
                attr.SetValue(new_value)
        
    def create_ui(self):
        def create_hole_input(parent, label, text_input):
            label_text = wx.StaticText(parent, label=label)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(label_text, 0, wx.CENTER)
            sizer.Add(text_input, 0, wx.CENTER)
            return sizer
            
        def create_ctrl(parent, number):
            text_ctrl = wx.TextCtrl(
                parent, id=int(number), style=wx.TE_CENTRE, size=size, 
                validator=self.get_validator())
            setattr(parent, f"input_{number}", text_ctrl)
        
        def create_row(hole_range):
            h_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for i in hole_range:
                number = ("0"+str(i))[-2:]
                create_ctrl(self, number)
                h_sizer.Add(
                    create_hole_input(
                        self, f"Hole {i}", getattr(self, f"input_{number}")
                    ), 0, wx.ALL, 2)
            return h_sizer 
        
        size = (50, -1)
        static_box = wx.StaticBox(self, wx.ID_ANY, label="Scorecard")
        self.sb_sizer = wx.StaticBoxSizer(static_box, orient=wx.VERTICAL)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button = wx.Button(self, label="Sumbit Changes", size=(200, -1))
        self.button.Bind(wx.EVT_BUTTON, self.on_button_press)
        self.sb_sizer.Add(create_row(range(1,10)))
        if self.num_of_holes == 18:
            self.sb_sizer.Add(create_row(range(10,19)))
        self.sb_sizer.Add(self.button, 0, wx.ALL|wx.CENTER, 5)
        self.v_sizer.Add(self.sb_sizer, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizerAndFit(self.v_sizer)
        
    def get_data(self):
        data = {}
        for i in range(1, self.num_of_holes+1):
            number = ("0"+str(i))[-2:]
            data[i] = getattr(self, f"input_{number}").GetValue()
        return data
    
    def validate(self):
        validation_list = []
        for i in range(1, self.num_of_holes+1):
            number = ("0"+str(i))[-2:]
            text_control = getattr(self, f"input_{number}")
            valid = text_control.GetValidator().Validate(text_control)
            validation_list.append(valid)
        if all(validation_list):
            return True
        else:
            msg = wx.MessageDialog(
                None, message=INPUT_ERROR_MSG, 
                caption="Save Failure", style=wx.ICON_ERROR)
            msg.ShowModal()
            msg.Destroy()
            return False
        
    def on_button_press(self, event):
        if self.validate():
            self.parent.data = self.get_data()
            self.Close()
        
# %%


