import pickle

class DebugUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        print(f"Loading class: {module}.{name}")
        return super().find_class(module, name)

    def load(self):
        try:
            return super().load()
        except Exception as e:
            print(f"Error during load: {e}")
            raise