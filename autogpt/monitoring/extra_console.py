import tkinter as tk
import multiprocessing as mp


class _ExtraConsole:
    close_message = '<<close>>'

    def __init__(self, title, width, height, text_color, background_color):
        self.message_queue = mp.Queue()
        self.root = tk.Tk()
        self.root.title(title)

        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(self.root, wrap=tk.WORD, fg=text_color, bg=background_color, state=tk.DISABLED,
                                   yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(expand=True, fill=tk.BOTH)

        self.scrollbar.config(command=self.text_widget.yview)

        self.root.geometry(f"{width}x{height}")
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.mainloop_stopped = False

    def start_mainloop(self):
        self._process_queue()
        self.root.mainloop()
        self.mainloop_stopped = True

    def _process_queue(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            if message == _ExtraConsole.close_message:
                self.close()
                return
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, f"{message}\n")
            self.text_widget.config(state=tk.DISABLED)
        self.root.after(100, self._process_queue)

    def print_message(self, message="Hello, this is your message!"):
        self.message_queue.put(message)

    def _close(self):
        self.root.destroy()

    def close(self):
        self.root.after(0, self._close)


def _run_extra_console(message_queue, title, width, height, text_color, background_color):
    app = _ExtraConsole(title, width, height, text_color, background_color)
    app.message_queue = message_queue
    app.start_mainloop()


class ExtraConsole:
    _open_consoles = []

    def __init__(self, title="Extra Console", width=400, height=300, text_color='red', background_color='black'):
        self.title = title
        self.message_queue = mp.Queue()
        self.mainloop_process = mp.Process(
            target=_run_extra_console,
            args=(
                self.message_queue, title, width, height, text_color, background_color
            )
        )
        ExtraConsole._open_consoles.append(self)
        self.mainloop_process.start()

    def print(self, message):
        self.message_queue.put(message)

    def close(self):
        self.message_queue.put(_ExtraConsole.close_message)
        self.mainloop_process.join()

    @staticmethod
    def close_all():
        for c in ExtraConsole._open_consoles:
            c.close()


if __name__ == "__main__":
    # TODO: test on linux, add linux implementation
    import time

    console = ExtraConsole()
    console.print("This is a custom message.")

    time.sleep(0.1)

    x = input('Enter something: ')
    console.print("Super long text " * 1000)
    y = input('Enter something else: ')

    print('closing')
    console.close()
    print('closed')
