# -*- coding: utf-8 -*-
"""
Created on Sat May 20 10:29:34 2023

@author: pizzacoin
"""

# %%

from ObjectListView import ColumnDefn
from ObjectListView import ObjectListView
import controller
import dialogs
import wx

# %%

class AppPanelMain(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.session = parent.session
        self.create_ui()
        
    def _create_button(self, sizer, label, function):
        size = (120, -1)
        button = wx.Button(self, label=label, size=size)
        button.Bind(wx.EVT_BUTTON, function)
        sizer.Add(button, 0, wx.CENTER)
        
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._create_button(sizer, "Add Score", self.on_button_01)
        self._create_button(sizer, "Record Round", self.on_button_02)
        self._create_button(sizer, "View All Rounds", self.on_button_03)
        self._create_button(sizer, "Add New Park", self.on_button_04)
        self._create_button(sizer, "View Round History", self.on_button_05)
        self._create_button(sizer, "View All Parks", self.on_button_06)
        
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def on_button_01(self, event):
        with dialogs.ScoreDialog(self) as dlg:
            dlg.ShowModal()
    
    def on_button_02(self, event):
        current_id = None
        if "round_id" in self.parent.data.keys():
            current_id = self.parent.data["round_id"]
        with dialogs.RoundDialog(self, self.parent.session) as dlg:
            dlg.ShowModal()
        if "round_id" in self.parent.data.keys():
            if current_id != self.parent.data["round_id"]:
                self.parent.panels[1].round_id = self.parent.data["round_id"]
                self.parent.panels[1].load_round(self.parent.data["round_id"])
                self.parent.on_panel_switch(1)
                self.parent.panels[1].update_round_results()
                print(self.parent.panels[1].round_id)
                 
    def on_button_03(self, event):
        self.parent.on_panel_switch(5)
    
    def on_button_04(self, event):
        with dialogs.ParkDialog(self) as dlg:
            dlg.ShowModal()  
    
    def on_button_05(self, event):
        self.parent.on_panel_switch(1)
        
    def on_button_06(self, event):
        self.parent.on_panel_switch(2)
        self.parent.panels[2].update_park_results()
        
            
# %%

class AppPanelCourse(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_ui()
        self.course = None
        self.data = None
        self.course_details = None
        self.round_details = None
        self.update_course_results()
        self.update_round_results()
    
    def load_course(self, course):
        self.course = course
        self.title.SetLabel(self.course.course_name)
        self.update_course_results()
        self.update_round_results()
    
    def update_course_results(self):
        self.course_details = []
        if self.course:
            self.course_details.append(controller.get_par_values(
                self.parent.session, self.course.course_id))
            tee_colors = controller.get_tee_color_values(
                self.parent.session, self.course.course_id)
            for tee_color in tee_colors:
                self.course_details.append(tee_color)
            
        self.course_olv.SetColumns([
            ColumnDefn("Hole", "center", 75, "description"),
            ColumnDefn("1", "center", 40, "value_01"),
            ColumnDefn("2", "center", 40, "value_02"),
            ColumnDefn("3", "center", 40, "value_03"),
            ColumnDefn("4", "center", 40, "value_04"),
            ColumnDefn("5", "center", 40, "value_05"),
            ColumnDefn("6", "center", 40, "value_06"),
            ColumnDefn("7", "center", 40, "value_07"),
            ColumnDefn("8", "center", 40, "value_08"),
            ColumnDefn("9", "center", 40, "value_09"),
            ColumnDefn("10", "center", 40, "value_10"),
            ColumnDefn("11", "center", 40, "value_11"),
            ColumnDefn("12", "center", 40, "value_12"),
            ColumnDefn("13", "center", 40, "value_13"),
            ColumnDefn("14", "center", 40, "value_14"),
            ColumnDefn("15", "center", 40, "value_15"),
            ColumnDefn("16", "center", 40, "value_16"),
            ColumnDefn("17", "center", 40, "value_17"),
            ColumnDefn("18", "center", 40, "value_18")])
        self.course_olv.useAlternateBackColors = False
        self.course_olv.SetObjects(self.course_details)
        self.Layout()
        
    def update_round_results(self):
        if self.course:
            self.round_details = controller.get_player_scores(
                self.parent.session, self.course.course_id)
        self.rounds_olv.SetColumns([
            ColumnDefn("Round ID", "center", 80, "round_id"),
            ColumnDefn("Player Name", "center", 150, "player_name"),
            ColumnDefn("Total Strokes", "center", 100, "total_strokes"),
            ColumnDefn("Tee Time", "center", 150, "tee_time")])
        self.rounds_olv.useAlternateBackColors = False
        self.rounds_olv.SetObjects(self.round_details)
        self.Layout()

    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title = wx.StaticText(self, label="<No Course Loaded>")
        self.title.SetFont(font)
        self.course_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.rounds_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.details_button = wx.Button(self, label="Details")
        self.back_button = wx.Button(self, label="Back")
        self.add_button = wx.Button(self, label="+", size=(40, -1))
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back_button)
        self.details_button.Bind(wx.EVT_BUTTON, self.on_details_button)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        button_sizer.Add(self.add_button, 0, wx.ALL, 5)
        button_sizer.Add(self.details_button, 0, wx.ALL, 5)
        button_sizer.Add(self.back_button, 0, wx.ALL, 5)
        sizer.Add(self.title, 0, wx.ALL, 5)
        sizer.Add(self.course_olv, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5)
        sizer.Add(self.rounds_olv, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5)
        sizer.Add(button_sizer, 0, wx.CENTER)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def on_back_button(self, event):
        self.parent.on_panel_switch(3)
        
    def on_details_button(self, event):
        course = self.course_olv.GetSelectedObject()
        if course:
            if course.description == "Par":
                self.on_par()
            else:
                color = course.description
                course_tee_id = course.keys["course_tee_id"]
                self.on_color(color, course_tee_id)
                
    def on_color(self, color, course_tee_id):
        self.data = None
        tee_colors = controller.get_tee_color_values(
            self.parent.session, self.course.course_id, color)
        for tee_color in tee_colors:
            if tee_color.description == color:
                selected_color = tee_color
        with dialogs.ScoreDialog(
            self, selected_color.to_dict(), self.course.no_of_holes, "distance"
        ) as dlg:
            dlg.ShowModal()
        if self.data:
            controller.update_distances(
                self.parent.session, self.course.course_id, 
                course_tee_id, self.data)
        self.update_course_results()
                
        
    def on_par(self):
        self.data = None
        par_values = controller.get_par_values(
            self.parent.session, self.course.course_id)
        with dialogs.ScoreDialog(
                self, par_values.to_dict(), self.course.no_of_holes, "par"
        ) as dlg:
            dlg.ShowModal()
            
        if self.data:
            controller.update_holes(
                self.parent.session, self.course.course_id, self.data)
        self.update_course_results()
        
    def on_add_button(self, event):
        with dialogs.CourseTeeDialog(self, self.course) as dlg:
            dlg.ShowModal()
        self.update_course_results()


# %%

class AppPanelPark(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_ui()
        self.park = None
        self.courses = []
        self.update_course_results()
    
    def load_park(self, park):
        self.park = park
        self.title.SetLabel(self.park.park_name)
        self.update_course_results()
        
    def update_course_results(self):
        if self.park:
            self.courses = controller.get_courses(
                self.parent.session, self.park.park_id)
        self.course_olv.SetColumns([
            ColumnDefn("CourseID", "center", 75, "course_id"),
            ColumnDefn("Course Name", "left", 220, "course_name"),
            ColumnDefn("Number of Holes", "center", 125, "no_of_holes"),
            ColumnDefn("Times Played", "right", 100, "times_played"),
            ColumnDefn("Par", "right", 60, "par")
        ])
        self.course_olv.useAlternateBackColors = False
        self.course_olv.SetObjects(self.courses)
        self.Layout()
    
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title = wx.StaticText(self, label="<No Park Loaded>")
        
        self.title.SetFont(font)
        
        self.add_button = wx.Button(self, label="+", size=(40, -1))
        
        self.course_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.course_button = wx.Button(self, label="Course Details")
        self.back_button = wx.Button(self, label="Back")
        self.course_button.Bind(wx.EVT_BUTTON, self.on_details_button)
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back_button)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        
        sizer.Add(self.title, 0, wx.ALL, 5)
        sizer.Add(self.course_olv, 1, wx.RIGHT|wx.LEFT|wx.EXPAND, 5)
        
        h_sizer.Add(self.add_button, 0, wx.ALL|wx.CENTER, 5)
        h_sizer.Add(self.course_button, 0, wx.ALL|wx.CENTER, 5)
        h_sizer.Add(self.back_button, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(h_sizer, 0, wx.CENTER)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def on_details_button(self, event):
        selected_course = self.course_olv.GetSelectedObject()
        if selected_course:
            self.parent.on_panel_switch(4)
            self.parent.panels[4].load_course(selected_course)
        
    def on_back_button(self, event):
        self.parent.on_panel_switch(2)
        
    def on_add_button(self, event):
        with dialogs.CourseDialog(self) as dlg:
            dlg.ShowModal() 
        self.update_course_results()
        
        


# %%

class AppPanelParks(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_ui()
        self.parks = []
        self.update_park_results()
        
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.park_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        sizer.Add(self.park_olv, 1, wx.EXPAND|wx.ALL, 5)
        
        enter_button = wx.Button(self, label="Enter")
        back_button = wx.Button(self, label="Back")
        add_button = wx.Button(self, label="+", size=(40, -1))
        enter_button.Bind(wx.EVT_BUTTON, self.on_enter_button)
        back_button.Bind(wx.EVT_BUTTON, self.on_back_button)
        add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        h_sizer.Add(add_button, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        h_sizer.Add(enter_button, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        h_sizer.Add(back_button, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        sizer.Add(h_sizer, 0, wx.CENTER)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def update_park_results(self):
        self.parks = controller.get_parks(self.parent.session)
        self.park_olv.SetColumns([
            ColumnDefn("ParkID", "center", 75, "park_id"),
            ColumnDefn("Park Name", "left", 220, "park_name"),
            ColumnDefn("County", "right", 80, "county"),
            ColumnDefn("Privacy Type", "right", 100, "privacy_type")
        ])
        self.park_olv.useAlternateBackColors = False
        self.park_olv.SetObjects(self.parks)
        self.Layout()
        
    def on_enter_button(self, event):
        selected_park = self.park_olv.GetSelectedObject()
        if selected_park:
            self.parent.on_panel_switch(3)
            self.parent.panels[3].load_park(selected_park)
        
    def on_back_button(self, event):
        self.parent.on_panel_switch(0)
        
    def on_add_button(self, event):
        with dialogs.ParkDialog(self) as dlg:
            dlg.ShowModal() 
        self.update_park_results()


# %%

class AppPanelRounds(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.session = parent.session
        self.rounds = []
        self.data = {}
        self.create_ui()
        self.update_list_view()
        
    def create_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_view = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.add_button = wx.Button(self, label="+", size=(40, -1))
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.details_button = wx.Button(self, label="Details", size=(100, -1))
        self.details_button.Bind(wx.EVT_BUTTON, self.on_details)
        self.back_button = wx.Button(self, label='Back', size=(100, -1))
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back)
        sizer.Add(self.list_view, 1, wx.ALL|wx.EXPAND, 5)
        
        button_sizer.Add(self.add_button, 0, wx.LEFT|wx.BOTTOM, 5)
        button_sizer.Add(self.details_button, 0, wx.LEFT|wx.BOTTOM, 5)
        button_sizer.Add(self.back_button, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        
        sizer.Add(button_sizer, 0, wx.CENTER)
        self.SetSizer(sizer)
        self.Layout()
        
    def update_list_view(self):
        self.rounds = controller.get_all_rounds(self.session)
        self.list_view.SetColumns([
            ColumnDefn("Round ID", "center", 75, "round_id"),
            ColumnDefn("Course Name", "left", 220, "course_name"),
            ColumnDefn("Number of Players", "left", 220, "number_of_players"),
            ColumnDefn("Best Score", "right", 60, "best_score"),
            ColumnDefn("Tee Time", "right", 60, "tee_time")])
        self.list_view.useAlternateBackColors = False
        self.list_view.SetObjects(self.rounds)
        
    def on_details(self, event):
        selected_round = self.list_view.GetSelectedObject()
        if selected_round:
            self.parent.on_panel_switch(1)
            self.parent.panels[1].load_round(selected_round.round_id)
        
    def on_add(self, event):
        with dialogs.RoundDialog(self, self.parent.session) as dlg:
            dlg.ShowModal()
        self.update_list_view()
        if "round_id" in self.data.keys():
            round_id = self.data["round_id"]
            with dialogs.PlayerDialog(self, round_id) as dlg:
                dlg.ShowModal()
            if "golfer_ids" in self.data.keys():
                controller.create_players(
                    self.session, round_id, self.data["golfer_ids"])
            self.parent.panels[1].load_round(round_id)
            self.parent.on_panel_switch(1)
    
    def on_back(self, event):
        self.parent.on_panel_switch(0)
        
        
# %%


class AppPanelRound(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.session = parent.session
        self.data = {}
        self.round_id = None
        self.players = []
        self.create_ui()
        self.update_round_results()
        
    def load_round(self, round_id):
        self.round_id = None
        round_info = controller.get_round_by_id(self.parent.session, round_id)
        if round_info:
            self.round_id = round_id
            course = controller.get_course_by_id(
                self.parent.session, round_info.CourseID)
            self.title_01.SetLabel(f"{course.CourseName}")
            self.update_round_results()
        
    def update_round_results(self):
        if self.round_id:
            self.players = controller.get_player_olv(
                self.parent.session, self.round_id)
        self.list_view.SetColumns([
            ColumnDefn("PlayerID", "center", 95, "player_id"),
            ColumnDefn("Player's Name", "left", 220, "player_name"),
            ColumnDefn("Score", "right", 60, "score"),
            ColumnDefn("Best Hole", "right", 100, "best_hole")
        ])
        self.list_view.useAlternateBackColors = False
        self.list_view.SetObjects(self.players)
    
    def create_ui(self): 
        sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title_01 = wx.StaticText(self, label="<No Record Loaded!>")
        self.edit_button = wx.Button(self, label="Edit Player(s)", size=(100,-1))
        self.back_button = wx.Button(self, label="Back", size=(100,-1))
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back)
        self.edit_button.Bind(wx.EVT_BUTTON, self.on_add_player)
        h_sizer.Add(self.edit_button, 0, wx.RIGHT, 5)
        h_sizer.Add(self.back_button, 0, wx.RIGHT, 5)
        
        
        sizer.Add(self.title_01, 0, wx.ALL|wx.EXPAND, 5)
        
        self.list_view = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        sizer.Add(self.list_view, 2, wx.ALL|wx.EXPAND, 5)
        sizer.Add(h_sizer, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.CENTER, 5)
        self.SetSizerAndFit(sizer)
        self.Layout()
        
    def on_add_player(self, event):
        with dialogs.PlayerDialog(self, self.round_id) as dlg:
            dlg.ShowModal()
        if "golfer_ids" in self.data.keys():
            controller.create_players(
                self.session, self.round_id, self.data["golfer_ids"])
            self.update_round_results()
            
    def on_back(self, event):
        self.parent.on_panel_switch(5)
            

# %%

class AppFrame(wx.Frame):
    def __init__(self):
        title = "Ultimate Golf Guide"
        super().__init__(None, title=title, size=(830, 400))
        self.session = controller.connect_to_database()
        self.create_menu()
        self.create_ui()
        self.data = {}

    def create_menu(self):
        menu_bar = wx.MenuBar() 
        file_menu = wx.Menu() 
        new_item = wx.MenuItem(
            file_menu, 1, text="&Main Menu", kind=wx.ITEM_NORMAL) 
        self.Bind(wx.EVT_MENU, self.on_menu, id=1)
        file_menu.Append(new_item)
        menu_bar.Append(file_menu, 'File') 
        self.SetMenuBar(menu_bar) 

    def create_ui(self):
        self.panels = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panels.append(AppPanelMain(self))
        self.panels.append(AppPanelRound(self))
        self.panels.append(AppPanelParks(self))
        self.panels.append(AppPanelPark(self))
        self.panels.append(AppPanelCourse(self))
        self.panels.append(AppPanelRounds(self))
        for panel in self.panels:
            self.sizer.Add(panel, 1, wx.EXPAND)
        for panel in self.panels[1:]:
            panel.Hide()
        self.SetSizer(self.sizer)
        self.Layout()
        
    def on_menu(self, event):
        self.on_panel_switch(0)
        
    def on_panel_switch(self, panel_id):
        for panel in self.panels:
            panel.Hide()
        self.panels[panel_id].Show()
        self.Layout()
        
# %%

if __name__ == "__main__":
    app = wx.App(False)
    frame = AppFrame()
    frame.Show()
    app.MainLoop()
    del app

# %%
