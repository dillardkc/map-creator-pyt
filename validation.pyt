class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        if self.params[0].value == "No":
            self.params[1].enabled = True
        else:
            self.params[1].enabled = False
        
        if self.params[0].value == "Yes":
            self.params[2].enabled = True
        else:
            self.params[2].enabled = False
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        if self.params[0].value == 'No' and self.params[1].value is not None:
            mapdate = self.params[1].value
            mapdate_str = mapdate.strftime("%Y%m%d")
            project_gdb_path = mapdate_str + '.gdb'
            if not arcpy.Exists(project_gdb_path):
                self.params[0].setErrorMessage("No gdb for selected date exists!")
            else:
                self.params[0].clearMessage() # Clear any previous warning
        if self.params[4].value is not None:
            input_string = str(self.params[4].value)
            if len(input_string) > 17:
                self.params[4].setErrorMessage("Input cannot exceed 17 characters.")
            else:
                self.params[4].clearMessage() # Clear any previous warning
        if self.params[5].value is not None:
            input_string = str(self.params[5].value)
            if len(input_string) > 30:
                self.params[5].setErrorMessage("Input cannot exceed 30 characters.")
            else:
                self.params[5].clearMessage() # Clear any previous warning
        if self.params[6].value is not None:
            input_string = str(self.params[6].value)
            if len(input_string) > 30:
                self.params[6].setErrorMessage("Input cannot exceed 30 characters.")
            else:
                self.params[6].clearMessage() # Clear any previous warning
        if self.params[7].value is not None:
            input_string = str(self.params[7].value)
            if len(input_string) > 30:
                self.params[7].setErrorMessage("Input cannot exceed 30 characters.")
            else:
                self.params[7].clearMessage() # Clear any previous warning
        return


    # def isLicensed(self):
    #     # set tool isLicensed.
    # return True
