import re
import sys
import os
import traceback
from pylxca_cmd import lxca_cmd
from pylxca_cmd.lxca_icommands import InteractiveCommand
from lxca_view import lxca_ostream
#from rlcompleter import readline
import itertools

PYTHON_SHELL = 99

from pylxca_cmd import lxca_icommands

class InteractiveShell(object):

    class help(InteractiveCommand):
        """
        Prints a list of available commands and their descriptions, or the help
        text of a specific command. Requires a list of the available commands in
        order to display text for them. 
        
        @ivar commands: A dictionary of available commands, bound to L{InteractiveShell.commands}
        @type commands: C{dict}
        """
        def __init__(self, commands):
            """
            Constructor function for L{_HelpCommand}.
            
            @param commands: A dictionary of available commands, usually L{InteractiveShell.commands}
            @type commands: C{dict}
            """
            self.commands = commands

        def handle_command(self, opts, args):
            """
            Prints a list of available commands and their descriptions if no
            argument is provided. Otherwise, prints the help text of the named
            argument that represents a command. Does not throw an error if the
            named argument doesn't exist in commands, simply prints a warning.
            
            @param opts: Will be an empty dictionary
            @type opts: C{dict}
            @param args: The raw string passed to the command, either a command or nothing
            @type args: C{list}
            
            @return: Returns nothing, sends messages to stdout
            @rtype: None
            """
            
            if len(args) == 0:
                self.do_command_summary( )
                return

            if args[0] not in self.commands:
                print 'No help available for unknown command "%s"' % args[0]
                return
            
            print self.commands[args[0]].get_help_message( )
            

        def do_command_summary(self):
            """
            If no command is given to display help text for specifically, then
            this helper method is called to print out a list of the available
            commands and their descriptions. Iterates over the list of commands,
            and gets their summary from L{lxca_icommands.get_short_desc}
            
            @return: Returns nothing, sends messages to stdout
            @rtype: C{None}
            """
            print 'The following commands are available:\n'

            cmdwidth = 0
            for name in self.commands.keys( ):
                if len(name) > cmdwidth:
                    cmdwidth = len(name)

            cmdwidth += 2
            for name in sorted(self.commands.keys( )):
                command = self.commands[name]

                if name == 'help':
                    continue
                
                print '  %s   %s' % (name.ljust(cmdwidth),
                                     command.get_short_desc( ))
                

        def get_short_desc(self):
            return ''
    
        def get_help_message(self):
            return ''

    class exit(InteractiveCommand):
        """
        Exits the interactive shell. 
        """

        def handle_command(self, opts, args):
            sys.exit(0)

        def get_short_desc(self):
            return 'Exit the program.'
    
        def get_help_message(self):
            return 'Type exit and the program will exit.  There are no options to this command'


    def __init__(self, 
        banner="Welcome to Interactive Shell",
        prompt=" >>> "):
        self.banner = banner
        self.prompt = prompt
        self.commands = { }
        self.ostream = lxca_ostream()
        self.add_command(self.help(self.commands))
        self.add_command(self.exit())
        
        self.add_command(lxca_cmd.connect(self))
        self.add_command(lxca_cmd.disconnect(self))
        self.add_command(lxca_cmd.log(self))
        self.add_command(lxca_cmd.chassis(self))
        self.add_command(lxca_cmd.nodes(self))
        self.add_command(lxca_cmd.switches(self))
        self.add_command(lxca_cmd.fans(self))
        self.add_command(lxca_cmd.powersupplies(self))
        self.add_command(lxca_cmd.fanmuxes(self))
        self.add_command(lxca_cmd.cmms(self))
        self.add_command(lxca_cmd.scalablesystem(self))
        self.add_command(lxca_cmd.ostream(self))
        self.add_command(lxca_cmd.jobs(self))

    def print_Hello(self):
        print "Hello"
        
    def add_command(self, command):
        if command.get_name( ) in self.commands:
            raise Exception, 'command %s already registered' % command.get_name( )

        self.commands[command.get_name()] = command

    def handle_input_args(self, command_name,*args, **kwargs):
        # Show message when no command
        if not command_name:
            return

        if not command_name in self.commands:
            print 'Unknown command: "%s". Type "help" for a list of commands.' % command_name
            return

        command = self.commands[command_name]

        opts = {}
        args = {}
       
        for item in kwargs['kwargs']:
            args['--' + item] = kwargs['kwargs'][item]
        
        try:
            return command.handle_command(opts=opts, args=list(itertools.chain(*args.items())))
        except Exception as err:
            print "Exception occurred while processing command."
            traceback.print_exc( )
            
    def handle_input(self, command_line):

        command_line = command_line.strip()

        # Get command
        command_args = ""
        if " " in command_line:
            command_line_index = command_line.index(" ")
            command_name = command_line[:command_line_index]
            command_args = command_line[command_line_index+1:]
        else:
            command_name = command_line

        # Show message when no command
        if not command_name:
            return

        if not command_name in self.commands:
            if (command_name == "pyshell"):
                return PYTHON_SHELL
            print 'Unknown command: "%s". Type "help" for a list of commands.' % command_name
            return
        

        command = self.commands[command_name]

        opts = {}
        args = []

        # Split the input to allow for quotes option values
        re_args = re.findall('\-\-\S+\=\"[^\"]*\"|\S+', command_args)
        # Parse args if present
        for i in xrange(0, len(re_args)):
            args.append( re_args[i] )
        try:
            return command.handle_command(opts=opts, args=args)
        except Exception as err:
            print "Exception occurred while processing command."
            traceback.print_exc( )
            
    """
    def auto_complete(self, text, state):
        command_list = self.commands.keys()
        re_space = re.compile('.*\s+$', re.M)
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in command_list][state]
        # account for last argument ending in a space
        if re_space.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in command_list:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in command_list if c.startswith(cmd)] + [None]
        return results[state]
    """
    
    def run(self):
        print
        print '-'*50
        print self.banner
        print 'Type "help" at any time for a list of commands.'
        print 'Type "pyshell" at any time to get interactive python shell'
        print '-'*50
        print

        while True:
            try:
#                readline.set_completer_delims(' \t\n;')
#                readline.parse_and_bind("tab: complete")
#                readline.set_completer(self.auto_complete)
                command_line = raw_input(self.prompt)
            except (KeyboardInterrupt, EOFError):
                break

            if self.handle_input(command_line) == PYTHON_SHELL:
                return PYTHON_SHELL
            else:
                continue
