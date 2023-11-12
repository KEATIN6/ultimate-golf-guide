# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 22:03:49 2023

@author: pizzacoin
"""

import wx

# %%


class ParkNameValidator(wx.Validator):
    def __init__(self, existing_values):
        super().__init__()
        self.existing_values = existing_values
        self.ending_words = ["Golf Course", "Golf Club", "Golf Resort"]
    
    def Clone(self):
         return ParkNameValidator(self.existing_values)
     
    def Validate(self, win):
       textCtrl = self.GetWindow()
       text = textCtrl.GetValue()
       if text in self.existing_values \
       or text == "" \
       or not text.endswith(tuple(self.ending_words)):
           textCtrl.SetBackgroundColour("pink")
           textCtrl.SetFocus()
           textCtrl.Refresh()
           return False
       else:
           textCtrl.SetBackgroundColour("white")
           textCtrl.Refresh()
           return True
    
    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True 
 
# %%
    
class DistanceValidator(wx.Validator):
     def __init__(self):
         super().__init__()

     def Clone(self):
         return DistanceValidator()

     def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if text.isnumeric() == False \
        or (0 if text == "" else int(text)) not in range(10, 700):
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour("white")
            textCtrl.Refresh()
            return True

     def TransferToWindow(self):
         return True

     def TransferFromWindow(self):
         return True 
     
# %%
        
class ParValidator(wx.Validator):
     def __init__(self):
         super().__init__()

     def Clone(self):
         return ParValidator()

     def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if text.isnumeric() == False \
        or (0 if text == "" else int(text)) not in range(1, 15):
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
        else:
            textCtrl.SetBackgroundColour("white")
            textCtrl.Refresh()
            return True

     def TransferToWindow(self):
         return True

     def TransferFromWindow(self):
         return True 
     
# %%

class ComboBoxValidator(wx.Validator):
     def __init__(self, options):
         super().__init__()
         self.options = options

     def Clone(self):
         return ComboBoxValidator(self.options)

     def Validate(self, win, options=None):
         if options:
             self.options=options
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         if text not in self.options:
             textCtrl.SetBackgroundColour("pink")
             textCtrl.SetFocus()
             textCtrl.Refresh()
             return False
         else:
            textCtrl.SetBackgroundColour("white")
            textCtrl.Refresh()
            return True
        
     def TransferToWindow(self):
         return True

     def TransferFromWindow(self):
         return True 
     
# %%