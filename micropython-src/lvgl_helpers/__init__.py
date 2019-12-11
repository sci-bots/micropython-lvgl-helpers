import functools as ft
import lvgl as lv


def children(parent):
    n = parent.count_children()
    if n:
        for i in range(n):
            child = parent.get_child(None if i == 0 else child)
            yield child
            
            
def children_recursive(parent):
    for child in children(parent):
        yield child
        for grandchild in children_recursive(child):
            yield grandchild 
            

# Automatically scroll view to show focused object.
def group_focus_cb(tab, group):
    f = lv.group_get_focused(group)
    lv.page.focus(tab, f, lv.ANIM.ON)
    
    
class InputsTabView(lv.tabview):
    def __init__(self, parent, drivers):
        super().__init__(parent)
        self.btns, self.content = list(children(self))
        self.drivers = drivers
        self._groups = []
        self._widgets = []
        self.set_event_cb(self.on_tab_selected)
        
    def add_widget(self, name, class_, *args, **kwargs):
        tab = self.add_tab(name)
        group = lv.group_create()
        lv.group_remove_all_objs(group)
        widget = class_(tab, *args, **kwargs)
        if hasattr(widget, 'input_children'):
            for c in widget.input_children():
                lv.group_add_obj(group, c)
        lv.group_set_refocus_policy(group, lv.GROUP_REFOCUS_POLICY.NEXT)
        lv.group_set_focus_cb(group, ft.partial(group_focus_cb, tab))
        self._groups.append(group)
        self._widgets.append(widget)
        self.on_tab_selected(self, lv.EVENT.VALUE_CHANGED)
        
    def on_tab_selected(self, tabview, event):
        if event == lv.EVENT.VALUE_CHANGED:
            i = self.get_tab_act()
            lv.group_remove_obj(self.btns)
            group = self._groups[i]
            lv.group_add_obj(group, self.btns)
            for driver in self.drivers:
                driver.group = group
            lv.group_set_editing(group, False)
    
    @property
    def tabs(self):
        return [self.get_tab(i) for i in range(self.get_tab_count())]


class InputsContainer(lv.cont):
    def __init__(self, parent, style=None):
        super().__init__(parent)
        if style is None:
            style = lv.style_t()
            lv.style_copy(style, lv.style_transp)
        self.set_style(lv.cont.STYLE.MAIN, style)
        self.set_layout(lv.LAYOUT.COL_L)
        self.set_fit(lv.FIT.FILL)
        
    def input_children(self):
        children_ = list(c for c in children_recursive(self)
                         if isinstance(c, (lv.spinbox, lv.btn)))
        return reversed(children_)