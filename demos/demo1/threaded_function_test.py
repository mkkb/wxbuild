import time
import wx


def threaded_monitor_function(*args, **kwargs):
    print('Just started this unkown thread....??', args, kwargs)
    thread_instance = kwargs['thread_instance']
    for i in range(12):
        time.sleep(1)
        print(" - i just slept 1 second...", )

        post_to_gui(f'Some data... {i}', thread_instance)
        gui_state = get_gui_state(thread_instance)
        print(" gui_state::", gui_state)

    print(" thread_inst::", thread_instance.wx_id, thread_instance.event_class)


def get_gui_state(thread_instance):
    pass

def post_to_gui(data, thread_instance):
    wx.PostEvent(thread_instance.parent, thread_instance.event_class(
        data=data, wx_id=thread_instance.wx_id
    ))