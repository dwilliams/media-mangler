#!/usr/bin/env python3

### IMPORTS ###

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class RootResource:
    def on_get(self, request, response):
        response.text = "Root Page.  Put UI here."
