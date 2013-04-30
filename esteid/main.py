import sys
from cliff.app import App
from cliff.commandmanager import CommandManager

class EsteidApp(App):
  def __init__(self):
    super(EsteidApp, self).__init__(description='Swiss army knife EstEID utility', version='0.1', command_manager=CommandManager('esteid.cli'))

def main(argv=sys.argv[1:]):
  myapp = EsteidApp()
  return myapp.run(argv)
        
        
if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
