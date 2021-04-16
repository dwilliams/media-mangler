#!/usr/bin/env python3

### IMPORTS ###
import logging
import os
import threading

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###

class PathWalker:
    _filename_ignore = [
        'WPSettings.dat',
        'IndexerVolumeGuid',
        '.windows',
        'Thumbs.db'
    ]

    def __init__(self, root_path, exclude_dirs = [], display_counts = True, stop_event = threading.Event()):
        self.logger = logging.getLogger(type(self).__name__)
        # FIXME: Update to use pathlib.Path
        self.root_path = root_path
        self.exclude_dirs = exclude_dirs
        self.display_counts = display_counts
        self._stop_event = stop_event # Needed to allow threads to end early on CTRL+C
        self._files_list = [] # List of dictionaries with 'dirpath' and 'filename' keys
        # ...
        self._walk_path()

    def __str__(self):
        return "PathWalker RootPath: {}".format(self.root_path)

    @property
    def files_list(self):
        return [os.path.join(item['dirpath'], item['filename']) for item in self._files_list]

    @property
    def files_list_dicts(self):
        return self._files_list

    def _walk_path(self):
        self.logger.debug("Walking Path: %s", self.root_path)
        for root, dirs, files in os.walk(self.root_path, topdown = True):
            # Breaking out early if stop_event is triggered
            if self._stop_event.is_set():
                self.logger.warning("Stopping Early")
                break
            # NOTES: makes sure to check each directory for an exclude as a full path or as a directory name
            # if d not in self.exclude_dirs or if os.path.join(root, d) not in self.exclude_dirs
            # dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            # FIXME: Need to work through the possible options for the exclude_dirs list
            #        - bare directories referenced to root_path
            #        - relative paths referenced to the root_path
            #        - absolute paths (should this be checked to be under the root_path
            #        Might be a good idea to brute force the scan instead of relying on os.walk
            for directory in list(dirs): # Wrapped in list() to make a new list so to not modify the for loop's list
                # Breaking out early if stop_event is triggered
                if self._stop_event.is_set():
                    self.logger.warning("Stopping Early")
                    break
                self.logger.debug("Checking directory '%s' against list '%s'", directory, self.exclude_dirs)
                self.logger.debug("Checking directory '%s' against list '%s'", os.path.join(root, directory), self.exclude_dirs)
                if directory in self.exclude_dirs:
                    dirs.remove(directory)
                elif os.path.join(root, directory) in self.exclude_dirs:
                    dirs.remove(directory)

            for filename in files:
                # Breaking out early if stop_event is triggered
                if self._stop_event.is_set():
                    self.logger.warning("Stopping Early")
                    break
                if filename not in self._filename_ignore:
                    #self.files_list.append(os.path.join(root, filename))
                    self._files_list.append({'dirpath': root, 'filename': filename})
                    if self.display_counts and len(self._files_list) % 99 == 0:
                        self.logger.info("%d files counted so far", len(self._files_list))
