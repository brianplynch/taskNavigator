from typing import Callable
from tkinter import Frame, Listbox, Button, END, OptionMenu, StringVar, Text
import logging
from datetime import datetime
from configparser import ConfigParser
from ux.colorspace import parse_color_description


type FilteredListCallback = Callable[[FilteredListFrame], None]


def unique_values(items: list) -> list:
    unique_items: list = list()
    for item in items:
        if unique_items.count(item) == 0:
            unique_items.append(item)
    return unique_items




def distribute_rows_and_columns(frame_object: Frame, row_weights: list[int], column_weights: list[int], min_height: int = 50) -> None:
    """
    Sets the frame_object's row weight (height-distribution) and column weight (width-distribution)
    
    frame_object: no type specified - a TK object, such as a frame, 
        which has the methods 'rowconfigure' and 'columnconfigure'

        rowconfigure(self, index: int, cnf={}, **kw)
    
    row_weights: list[int] - for each row in the frame_object define a weight, 
        e.g. for 3 rows [1, 8, 1] would define row weights of 10% for the top row, 
        80% for the middle row, and 10% for the bottom row
    
    column_weights: list[int] - same concept as for row_weights, but for columns

    Return: None
    """
    for row, weight in enumerate(row_weights):
        frame_object.rowconfigure(row, weight=weight, uniform='tag', minsize=min_height)
    for col, weight in enumerate(column_weights):
        frame_object.columnconfigure(col, weight=weight, uniform='tag')


class FilteredListFrame(Frame):
    def __init__(self, master, all_objects: list[object]):
        super().__init__(master)

        # Configure Appearance
        config_attributes = ConfigParser()
        config_attributes.read('./ux/filtered_list_frame_attributes.ini')
        config_attributes['app']['background_color']
        self.app_background_color = parse_color_description(config_attributes['app']['background_color']).hex
        self.action_widget_background_color = parse_color_description(config_attributes['action_widget']['background_color']).hex
        self.action_widget_font_type = config_attributes['font']['typeface']
        self.action_widget_font_size = int(config_attributes['font']['size'])
        self.action_widget_font_color = parse_color_description(config_attributes['action_widget']['font_color']).hex
        
        self.inactive_highlight_color = parse_color_description('Black').hex
        self.active_highlight_color = parse_color_description(config_attributes['entry_widget']['highlight_color']).hex

        
        self.entry_box_attributes = {
            'bg': config_attributes['entry_widget']['background_color'],
            'fg': config_attributes['entry_widget']['font_color'],
            'font': (self.action_widget_font_type, self.action_widget_font_size)
            }
        
        self.list_box_attributes = {
            'bg': config_attributes['entry_widget']['background_color'],
            'fg': config_attributes['entry_widget']['font_color'],
            'font': (self.action_widget_font_type, self.action_widget_font_size),
            "selectbackground": self.active_highlight_color,
            "selectmode": "SINGLE"
        }
        
        self.padding_attributes = {}
        

        # Data

        self._all_objects: list = all_objects
        self._all_objects_display_text: list[str] = [str(obj) for obj in self._all_objects]
        self._all_text_object_map: dict[str,object] = dict(zip(self._all_objects_display_text, self._all_objects))
        self._filtered_objects: list = self.all_objects
        self._filtered_objects_display_text = [str(obj) for obj in self._filtered_objects]
        self._filtered_text_object_map: dict[str,object] = dict(zip(self._filtered_objects_display_text, self._filtered_objects))
        self.action_callbacks: dict[str, Callable[[FilteredListFrame], None]] = dict()
        self._filter_pattern: str = ""
        self._regex_enabled: bool = True
        self._selected_item_text: str = self._all_objects_display_text[0] if self._all_objects_display_text else ""
        self._saved_filters: list[str] = [
            "",
            "state:started",
            "state:blocked",
            "state:planned",
            f"results:{datetime.now().strftime('%Y%m%d')}",
            "-assignee:Brian Lynch"
            ]

        # Create UI
        self.filter_definition_frame: Frame = Frame(self, bg=self.app_background_color)

        self.filter_entry_frame: Frame = Frame(self.filter_definition_frame, bg=self.app_background_color)
        self.filter_entry: Text = Text(self.filter_entry_frame, wrap="word", width=20, height=2, **self.entry_box_attributes)
        self.filter_entry.config(insertbackground=self.action_widget_font_color)
        self.filter_entry_callback = self.open_saved_filters_dropdown
        self.filter_entry.bind("<ButtonRelease-3>", self.filter_entry_right_click)
        
        self.filter_entry_button_frame: Frame = Frame(self.filter_definition_frame, bg=self.app_background_color)
        self.filter_entry_button: Button = Button(self.filter_entry_button_frame, text="ok", command=self.update_filter_definition)
        self.filter_entry_button.configure(bg=self.action_widget_background_color, fg=self.action_widget_font_color, font=(self.action_widget_font_type, self.action_widget_font_size))

        self.filtered_list_selector_frame: Frame = Frame(self, bg=self.app_background_color)
        self.filtered_list_selector: Listbox = Listbox(self.filtered_list_selector_frame, **self.list_box_attributes)
        self.filtered_list_selector.bind("<<ListboxSelect>>", self.handle_filtered_list_left_click_event)
        self.filtered_list_selector.bind("<Double-1>", self.handle_filtered_list_double_click_event)
        self.filtered_list_selector.bind("<ButtonRelease-2>", self.handle_filtered_list_middle_click_event)
        self.filtered_list_selector.bind("<ButtonRelease-3>", self.handle_filtered_list_right_click_event)
        logging.debug(f"FONT: {self.filtered_list_selector.cget('font')}")

        # initialize the callbacks
        self.filtered_list_double_click_callback = lambda t: logging.debug("double-click has not been binded")
        self.filtered_list_middle_click_callback = lambda t: logging.debug("middle-click has not been binded")
        self.filtered_list_right_click_callback = self.open_action_dropdown

        self.action_button_frame: Frame = Frame(self, bg=self.app_background_color)
        self.selected_action = StringVar(self.action_button_frame)
        self.selectable_actions = []
        self.action_dropdown: OptionMenu = OptionMenu(self.action_button_frame, self.selected_action, self.selectable_actions)
        self.action_dropdown.configure(bg=self.action_widget_background_color, fg=self.action_widget_font_color, font=(self.action_widget_font_type, self.action_widget_font_size))
        self.action_dropdown["menu"].configure(bg=self.action_widget_background_color, fg=self.action_widget_font_color, font=(self.action_widget_font_type, self.action_widget_font_size))

        self.filtered_objects = self.all_objects

        self.child_filtered_list_frame = None
        self.parent_filtered_list_frame = None

        # Arrange UI

        self.grid(self.padding_attributes, row=0, column=0, sticky="nsew")

        self.filter_definition_frame.grid(self.padding_attributes, row=0, column=0, sticky="nsew")
        self.filter_entry_frame.grid(self.padding_attributes, row=0, column=0, sticky="nsew")
        self.filter_entry_button_frame.grid(self.padding_attributes, row=0, column=1, sticky="nsew")

        self.filter_entry.grid(self.padding_attributes, row=0, column=0, sticky="nsew")
        self.filter_entry_button.grid(self.padding_attributes, row=0, column=0, sticky="nsew")

        self.filtered_list_selector_frame.grid(self.padding_attributes, row=1, column=0, sticky="nsew")
        self.filtered_list_selector.grid(self.padding_attributes, row=0, column=0, sticky="nsew")

        #self.action_button_frame.grid(self.padding_attributes, row=2, column=0, sticky="nsew")
        #self.action_dropdown.grid(self.padding_attributes, row=0, column=0, sticky="nsew")
        
        distribute_rows_and_columns(self.filter_entry_frame, [1], [1], min_height=50)
        distribute_rows_and_columns(self.filter_entry_button_frame, [1], [1], min_height=50)
        distribute_rows_and_columns(self.filter_definition_frame, [1], [9, 1], min_height=50)
        distribute_rows_and_columns(self.filtered_list_selector_frame, [1], [1], min_height=50)
        distribute_rows_and_columns(self, [5, 20], [1], min_height=50)
        #distribute_rows_and_columns(self.action_button_frame, [1], [1])

    def __repr__(self) -> str:
        if not self.all_objects:
            return f"filtered_list_frame[no objects]"
        object_type_name = type(self.all_objects[0]).__name__
        return f"filtered_list_frame[{object_type_name}]"

    @property
    def all_objects(self) -> list:
        return self._all_objects
    
    @all_objects.setter
    def all_objects(self, new_base_list: list) -> None:
        """When base list is updated, the filtered list is also updated"""
        self._all_objects = new_base_list
        self.apply_filter(self.filter_pattern)
        self._all_objects_display_text = [str(obj) for obj in self._all_objects]
        self._all_text_object_map: dict[str,object] = dict(zip(self._all_objects_display_text, self._all_objects))

    
    def set_base_list(self, new_base_list: list) -> None:
        self.all_objects = new_base_list

    @property
    def filtered_objects(self) -> list:
        """a list of objects which are shown as the __str__ representation"""
        return self._filtered_objects
    
    @filtered_objects.setter
    def filtered_objects(self, new_filtered_list: list) -> None:
        if new_filtered_list:
            self._filtered_objects = new_filtered_list
            filtered_list_idents = [str(item) for item in self._filtered_objects]
        else:
            self._filtered_objects = []
            filtered_list_idents = [""]

        self._filtered_objects_display_text = filtered_list_idents
        self._filtered_text_object_map: dict[str,object] = dict(zip(self._filtered_objects_display_text, self._filtered_objects))

        self.populate_listbox(self.filtered_list_selector, filtered_list_idents)
        if new_filtered_list:
            self.selected_item_text = self.selected_item_text if self.selected_item_text in self._filtered_objects_display_text else str(self._filtered_objects[0])
    
    def set_filtered_list(self, new_filtered_list: list) -> None:
        self.filtered_objects = new_filtered_list

    @property
    def regex_enabled(self) -> bool:
        return self._regex_enabled
    
    @regex_enabled.setter
    def regex_enabled(self, new_regex_enabled: bool) -> None:
        self._regex_enabled = new_regex_enabled

    @property
    def filter_pattern(self) -> str:
        return self._filter_pattern
    
    @filter_pattern.setter
    def filter_pattern(self, new_filter_pattern: str) -> None:
        self.set_entry(self.filter_entry, new_filter_pattern)
        self._filter_pattern = new_filter_pattern
        
    def set_filter_pattern(self, new_filter_pattern: str) -> None:
        self.filter_pattern = new_filter_pattern
        self.update_filter_definition()

    @property
    def selected_item_text(self) -> str:
        return self._selected_item_text
    
    @selected_item_text.setter
    def selected_item_text(self, new_selected_item: str) -> None:
        self._selected_item_text = new_selected_item
        self.set_selection_listbox(self.filtered_list_selector, new_selected_item)

    def set_selected_item(self, new_selected_item: str) -> None:
        if self.filtered_objects == []:
            return
        if new_selected_item not in [str(item) for item in self.filtered_objects]:
            self.apply_filter(new_selected_item)
        self.selected_item_text = new_selected_item
        

    @property
    def selected_item_object(self):
        if not self._all_objects_display_text:
            self.display_message_to_user("nothing selected")
            raise RuntimeError("Nothing selected in empty selector")
        if not self.selected_item_text:
            _selected_item_text = self._all_objects_display_text[0]
        else:
            _selected_item_text = self.selected_item_text
        
        _selected_item_object = self._all_text_object_map[_selected_item_text]

        return _selected_item_object

    def apply_filter(self, filter_pattern: str, regex_enabled: bool = False) -> None:
        _filtered_list = self.parse_and_apply_filter_pattern(filter_pattern, regex_enabled)
        self.filtered_objects = _filtered_list

    def get_filter_function_from_pattern(self, condition: str):
        """
        expected pattern format is 
            attribute1:value1
        """
        not_condition = condition.startswith("-")
        if not_condition:
            condition = condition[1:]
        
        if ":" in condition:
            attribute_name, attribute_value = tuple(map(str.strip, condition.split(":")))
            if hasattr(self.all_objects[0], attribute_name):
                if not_condition:
                    filter_function = lambda o: attribute_value.lower() not in str(getattr(o, attribute_name)).lower()
                else:
                    filter_function = lambda o: attribute_value.lower() in str(getattr(o, attribute_name)).lower()

            else:
                if not_condition:
                    filter_function = lambda o: attribute_value not in str(o).lower()
                else:
                    filter_function = lambda o: attribute_value in str(o).lower()
        else:
            if not_condition:
                filter_function = lambda o: condition in str(o).lower()
            else:
                filter_function = lambda o: condition in str(o).lower()
        return filter_function

    def get_filter_function_from_regex(self, regex_filter_pattern: str):
        pass
    
    def get_items_from_condition(self, condition: str, items: list):
        filtered_items = items.copy()
        filter_function = self.get_filter_function_from_pattern(condition)
        filtered_items = list(filter(filter_function, filtered_items))
        unique_filtered_items = unique_values(filtered_items)
        return unique_filtered_items

    def get_items_from_ored_conditions(self, ored_conditions: list[str], items: list) -> list:
        filtered_groups = list()
        filtered_items = list()
        for condition in ored_conditions:
            filter_function = self.get_filter_function_from_pattern(condition)
            filtered_groups.append(list(filter(filter_function, items)))
        for filtered_group in filtered_groups:
            filtered_items.extend(filtered_group)
        unique_filtered_items = unique_values(filtered_items)
        return unique_filtered_items

    def get_items_from_anded_conditions(self, anded_conditions: list[str], items: list) -> list:
        filtered_items = items.copy()
        for condition in anded_conditions:
            filter_function = self.get_filter_function_from_pattern(condition)
            filtered_items = list(filter(filter_function, filtered_items))
        unique_filtered_items = unique_values(filtered_items)
        return unique_filtered_items

    def parse_and_apply_filter_pattern(self, filter_pattern: str, regex_enabled: bool = False) -> list:
        """Filters the base list based on the filter pattern and returns the filtered list
        filter_pattern: str - the pattern to filter the list by. 
            This may query object attributes using a colon e.g. "attribute_name:attribute_value"
            if the object attribute does not exist for the type contained in the list, 
                then the value is checked if it is in the __str__ attribute of the object
            comma-separated values are treated as ANDed conditions e.g. "attribute_name:attribute_value,age:25"
        regex_enabled: bool - if True, the filter pattern is treated as a regex pattern
        return: list[str] - the filtered list"""
        filtered_list = self.all_objects

        if regex_enabled:
            pass

        filter_pattern = str(filter_pattern).lower()

        # comma-separated query means conditions are ANDed, pipe (|) separated query means ORed conditions (only handle 1 type)
        if "," in filter_pattern and "|" in filter_pattern:
            self.display_message_to_user("Cannot have mixed AND + OR conditions")
            raise ValueError("Cannot have mixed AND + OR conditions")

        if "," in filter_pattern:
            filter_conditions = filter_pattern.split(",")
            filtered_list = self.get_items_from_anded_conditions(filter_conditions, self.all_objects)
        elif "|" in filter_pattern:
            filter_conditions = filter_pattern.split("|")
            filtered_list = self.get_items_from_ored_conditions(filter_conditions, self.all_objects)
        else:
            filter_conditions = filter_pattern
            filtered_list = self.get_items_from_condition(filter_conditions, self.all_objects)

        return filtered_list

    def bind_action_button(self, callback: Callable[..., None], button_label: str = "Action") -> None:
        self.action_button.configure(command=lambda *args: callback())
        self.action_button.configure(text=button_label)

    def select_action(self, option):
        """Call the registered callback function that takes the FilteredListFrame object as an input and returns None"""
        self.selected_action.set(option)
        self.action_callbacks[self.selected_action.get()](self)

    def open_action_dropdown(self, *text) -> None:
        x = self.filtered_list_selector.winfo_rootx()
        y = self.filtered_list_selector.winfo_rooty()
        self.action_dropdown["menu"].post(x,y)

    def create_filters_dropdown(self):
        self.filter_dropdown_selection: str = ""
        saved_filters_dropdown = OptionMenu(None, self.filter_dropdown_selection, "")
        saved_filters_menu=saved_filters_dropdown["menu"]
        saved_filters_menu.configure(bg=self.action_widget_background_color, fg=self.action_widget_font_color, font=(self.action_widget_font_type, self.action_widget_font_size))
        saved_filters_menu.delete(0,"end")
        for saved_filter in self._saved_filters:
            saved_filters_menu.add_command(label=saved_filter, command=lambda value=saved_filter: self.select_saved_filter(value))
        return saved_filters_menu

    def open_saved_filters_dropdown(self, *text) -> None:
        #logging.debug("dummy execute: open_saved_filters_dropdown()")
        menu = self.create_filters_dropdown()
        x = self.filter_entry.winfo_rootx()
        y = self.filter_entry.winfo_rooty()
        menu.post(x,y)

    def select_saved_filter(self, saved_filter: str) -> None:
        self.set_entry(self.filter_entry, saved_filter)
        self.update_filter_definition()

    def register_menu_function(self, menu_display_text: str, command_callback: FilteredListCallback):
        self.selectable_actions.append(menu_display_text)
        self.action_callbacks.update({menu_display_text: command_callback})

    def bind_registered_actions_to_dropdown(self) -> None:
        menu=self.action_dropdown["menu"]
        menu.delete(0,"end")
        for option in self.selectable_actions:
            menu.add_command(label=option, command=lambda value=option: self.select_action(value))
        #self.selected_action.trace_add("write", self.select_action)

    def bind_filter_entry_right_click(self, callback: Callable[..., None]) -> None:
        self.filter_entry_callback = callback

    def bind_filtered_list_left_click(self, callback: FilteredListCallback) -> None:
        self.filtered_list_left_click_callback: FilteredListCallback = callback

    def bind_filtered_list_double_click(self, callback: FilteredListCallback) -> None:
        self.filtered_list_double_click_callback = callback

    def bind_filtered_list_middle_click(self, callback: FilteredListCallback) -> None:
        self.filtered_list_middle_click_callback = callback

    def bind_filtered_list_right_click(self, callback: FilteredListCallback) -> None:
        self.filtered_list_right_click_callback = callback

    def handle_filtered_list_left_click_event(self, *event) -> None:
        if not self.filtered_list_selector.curselection():
            return
        self.selected_item_text = self.get_selection_listbox(self.filtered_list_selector)[0]
        if self.filtered_list_left_click_callback is not None:
            self.filtered_list_left_click_callback(self)

    def handle_filtered_list_double_click_event(self, *event) -> None:
        if not self.filtered_list_selector.curselection():
            logging.debug("Double Click Event processed; but, unexpectedly there is no cursor selection")
        self.selected_item_text = self.get_selection_listbox(self.filtered_list_selector)[0]
        if self.filtered_list_double_click_callback is not None:
            self.filtered_list_double_click_callback(self)
        
    def handle_filtered_list_middle_click_event(self, event) -> None:
        #set listbox selection to clicked item
        self.filtered_list_selector.selection_clear(0,END)
        self.filtered_list_selector.selection_set(self.filtered_list_selector.nearest(event.y))
        self.filtered_list_selector.activate(self.filtered_list_selector.nearest(event.y))

        self.selected_item_text = self.get_selection_listbox(self.filtered_list_selector)[0]
        if self.filtered_list_middle_click_callback is not None:
            self.filtered_list_middle_click_callback(self)

    def handle_filtered_list_right_click_event(self, event) -> None:
        #set listbox selection to clicked item
        self.filtered_list_selector.selection_clear(0,END)
        self.filtered_list_selector.selection_set(self.filtered_list_selector.nearest(event.y))
        self.filtered_list_selector.activate(self.filtered_list_selector.nearest(event.y))

        self.selected_item_text = self.get_selection_listbox(self.filtered_list_selector)[0]
        if self.filtered_list_right_click_callback is not None:
            self.filtered_list_right_click_callback(self)
    
    def filter_entry_right_click(self, event) -> None:
        self.filter_entry_callback()

    def set_child_filtered_list_frame(self, filtered_list_frame: FilteredListFrame) -> None:
        if filtered_list_frame.parent_filtered_list_frame:
            if filtered_list_frame.parent_filtered_list_frame is not self:
                raise RuntimeError(f"the child filtered_list_frame {filtered_list_frame}\n\talready has a parent defined\n{filtered_list_frame.parent_filtered_list_frame}")
        
        self.child_filtered_list_frame = filtered_list_frame
        filtered_list_frame.set_parent_filtered_list_frame(self)

    def set_parent_filtered_list_frame(self, filtered_list_frame: FilteredListFrame) -> None:
        if filtered_list_frame.child_filtered_list_frame:
            if filtered_list_frame.child_filtered_list_frame is not self:
                raise RuntimeError(f"the parent filtered_list_frame {filtered_list_frame}\n\talready has a child defined\n{filtered_list_frame.child_filtered_list_frame}")
        self.parent_filtered_list_frame = filtered_list_frame

    def bind_reload(self, reload_callback: FilteredListCallback) -> None:
        self.reload_callback = reload_callback

    def reload(self) -> None:
        try:
            self.reload_callback(self)
        except RuntimeError as er:
            # if there are no objects in the object list then nothing to reload
            logging.debug(er.args)

    def update_filter_definition(self, *event) -> None:
        # set the saved filters to itself with the new filter appended and all duplicates removed
        self.filter_pattern = self.consume_entry(self.filter_entry)
        self._saved_filters = list(set(self._saved_filters.copy() + [self.filter_pattern]))
        self.apply_filter(self.filter_pattern, self.regex_enabled)

    def get_text_input(self, *event) -> str:
        text_input = self.consume_entry(self.filter_entry)
        return text_input

    def highlight_listbox_item(self, list_box: Listbox, index: int, inactive_index: list[int]) -> None:
        # Reset all items to normal background color
        for idx in range(len(list_box.get(0,END))):
            list_box.itemconfig(idx, {'bg':self.action_widget_background_color})
        
        # Highlight inactive indices
        for idx in inactive_index:
            list_box.itemconfig(idx, {'bg':self.inactive_highlight_color})

        # Highlight active selection
        list_box.itemconfig(index, {'bg':self.active_highlight_color})

    def populate_listbox(self, list_box: Listbox, items: list[str]):
        list_box.delete(0, END)        
        for index, item in enumerate(items):
            list_box.insert(index + 1, item)
            
    def consume_entry(self, entry_box: Text) -> str:
        input_string = entry_box.get("1.0", END).strip()
        entry_box.delete("1.0", END)
        return input_string

    def set_entry(self, entry_box: Text, value: str) -> None:
        entry_box.delete("1.0", END)
        entry_box.insert("1.0", value)

    def get_selection_listbox(self, target_listbox: Listbox) -> list:
        """returns a list of strings of the selected items from the provided listbox
        if there is no selection, then returns a list with one empty string
        """
        if not target_listbox.curselection():
            return [""]
        else:
            selected_indicies = target_listbox.curselection()[0], target_listbox.curselection()[-1]

        selected_items_text = target_listbox.get(*selected_indicies)

        # .get returns either a tuple or a string, need to convert these to a list
        if isinstance(selected_items_text, str):
            selected_items_list = [selected_items_text]
        elif isinstance(selected_items_text, tuple):
            selected_items_list = list(selected_items_text)
        else:
            logging.debug(f"{selected_items_text=}, this is of type - {type(selected_items_text)}, but the selected_items_text must be a str or tuple")
            return [""]

        return selected_items_list
    
    def set_selection_listbox(self, target_listbox: Listbox, selection: str) -> None:
        target_listbox_items = target_listbox.get(0, END)
        if selection not in target_listbox_items:
            selection = self.get_selection_listbox(target_listbox)[0]
            if selection == "":
                return
        selection_index = target_listbox_items.index(selection)
        #target_listbox.activate(selection_index)

        self.highlight_listbox_item(target_listbox, selection_index, [])


    def display_message_to_user(self, message: str) -> None:
        self.set_entry(self.filter_entry, message)
