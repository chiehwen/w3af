'''
textFile.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

from core.controllers.basePlugin.baseOutputPlugin import baseOutputPlugin
from core.controllers.w3afException import w3afException
import core.data.kb.config as cf

# options
from core.data.options.option import option
from core.data.options.optionList import optionList

# severity constants for vuln messages
import core.data.constants.severity as severity

import sys
import time
import os


class textFile(baseOutputPlugin):
    '''
    Prints all messages to a text file.
    
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''
    
    def __init__(self):
        baseOutputPlugin.__init__(self)
        
        # User configured parameters
        self._file_name = 'output.txt'
        self._http_file_name = 'output-http.txt'
        self.verbose = True
        
        # Internal variables
        self._flush_counter = 0
        self._flush_number = 10
        self._initialized = False
        # File handlers
        self._file = None
        self._http = None
        # XXX Only set '_show_caller' to True for debugging purposes. It
        # causes the execution of potentially slow code that handles
        # with introspection. 
        self._show_caller = False

    def _init( self ):
        self._initialized = True
        try:
            #self._file = codecs.open( self._file_name, "w", "utf-8", 'replace' )
            self._file = open( self._file_name, "w")
        except IOError, io:
            msg = 'Can\'t open report file "' + os.path.abspath(self._file_name) + '" for writing'
            msg += ': "' + io.strerror + '".'
            raise w3afException( msg )
        except Exception, e:
            msg = 'Can\'t open report file "' + self._file_name + '" for writing. Exception: "'
            msg += str(e) + '".'
            raise w3afException( msg )
            
        try:
            # Images aren't ascii, so this file that logs every request/response, will be binary
            #self._http = codecs.open( self._http_file_name, "wb", "utf-8", 'replace' )
            self._http = open( self._http_file_name, "wb" )
        except IOError, io:
            msg = 'Can\'t open report file "' + os.path.abspath(self._http_file_name) + '" for writing'
            msg += ': "' + io.strerror + '".'
            raise w3afException( msg )
        except Exception, e:
            msg = 'Can\'t open report file "' + self._http_file_name + '" for writing. Exception: "'
            msg += str(e) + '".'
            raise w3afException( msg )
        
    def __del__(self):
        if self._file is not None:
            self._file.close()
    
    def _write_to_file( self, msg ):
        '''
        Write to the log file.
        
        @parameter msg: The text to write.
        '''
        try:
            self._file.write( self._cleanString(msg) )
        except Exception, e:
            print 'An exception was raised while trying to write to the output file:', e
            sys.exit(1)
        
    def _write_to_HTTP_log( self, msg ):
        '''
        Write to the HTTP log file.
        
        @parameter msg: The text to write (a string representation of the HTTP req and res)
        '''
        try:
            self._http.write(msg)
        except Exception, e:
            print 'An exception was raised while trying to write to the HTTP'
            ' log output file:', e
            sys.exit(1)
            
    def write(self, message, log_type, newLine = True ):
        '''
        Method that writes stuff to the textFile.
        
        @param message: The message to write to the file
        @param log_type: Type of message are we writing to the file
        @param newLine: Add a new line after the message
        '''
        if not self._initialized:
            self._init()
        
        to_print = str(message)
        if newLine == True:
            to_print += '\n'
        
        now = time.localtime(time.time())
        the_time = time.strftime("%c", now)
        
        if self._show_caller:
            timestamp = '[%s - %s - %s] ' % (the_time, log_type, self.getCaller())
        else:
            timestamp = '[%s - %s] ' % (the_time, log_type)
            
        self._write_to_file( timestamp + to_print )

        self._flush()
    
    def debug(self, message, newLine = True ):
        '''
        This method is called from the output object. The output object was called from a plugin
        or from the framework. This method should take an action for debug messages.
        '''
        if self.verbose:
            self.write( message, 'debug', newLine)
            
    def information(self, message , newLine = True ):
        '''
        This method is called from the output object. The output object was called from a plugin
        or from the framework. This method should take an action for informational messages.
        '''
        self.write( message, 'information', newLine)

    def error(self, message , newLine = True ):
        '''
        This method is called from the output object. The output object was called from a plugin
        or from the framework. This method should take an action for error messages.
        '''
        self.write( message, 'error', newLine)     

    def vulnerability(self, message , newLine=True, severity=severity.MEDIUM ):
        '''
        This method is called from the output object. The output object was called from a plugin
        or from the framework. This method should take an action when a vulnerability is found.
        '''
        self.write( message, 'vulnerability', newLine)
        
    def console( self, message, newLine = True ):
        '''
        This method is used by the w3af console to print messages to the outside.
        '''
        self.write( message, 'console', newLine)
        
    def logEnabledPlugins(self,  plugins_dict,  options_dict):
        '''
        This method is called from the output manager object. This method should take an action
        for the enabled plugins and their configuration. Usually, write the info to a file or print
        it somewhere.
        
        @parameter pluginsDict: A dict with all the plugin types and the enabled plugins for that
                                               type of plugin.
        @parameter optionsDict: A dict with the options for every plugin.
        '''
        now = time.localtime(time.time())
        the_time = time.strftime("%c", now)
        timestamp = '[ ' + the_time + ' - Enabled plugins ] '
        
        to_print = ''
        
        for plugin_type in plugins_dict:
            to_print += self._create_plugin_info( plugin_type, plugins_dict[plugin_type], 
                                                                  options_dict[plugin_type])
        
        # And now the target information
        str_targets = ', '.join( [u.url_string for u in cf.cf.getData('targets')] )
        to_print += 'target\n'
        to_print += '    set target ' + str_targets + '\n'
        to_print += '    back'
        
        to_print = to_print.replace('\n', '\n' + timestamp ) + '\n'
        
        self._write_to_file( timestamp + to_print )
    
    def _create_plugin_info(self, plugin_type, plugins_list, plugins_options):
        '''
        @return: A string with the information about enabled plugins and their options.
        
        @parameter plugin_type: audit, discovery, etc.
        @parameter plugins_list: A list of the names of the plugins of plugin_type that are enabled.
        @parameter plugins_options: The options for the plugins
        '''
        response = ''
        
        # Only work if something is enabled
        if plugins_list:
            response = 'plugins\n'
            response += '    ' + plugin_type + ' ' + ', '.join(plugins_list) + '\n'
            
            for plugin_name in plugins_list:
                if plugins_options.has_key(plugin_name):
                    response += '    ' + plugin_type + ' config ' + plugin_name + '\n'
                    
                    for plugin_option in plugins_options[plugin_name]:
                        name = str(plugin_option.getName())
                        value = str(plugin_option.getValue())
                        response += '        set ' + name + ' ' + value + '\n'
                    
                    response += '        back\n'
            
            response += '    back\n'
            
        # The response
        return response
    
    def _flush(self):
        '''
        textfile.flush is called every time a message is sent to this plugin.
        self._file.flush() is called every self._flush_number
        '''
        if self._flush_counter % self._flush_number == 0:
            #   TODO: Remove this if I discover that it wasn't really needed.
            #   I just commented this because after some profiling I found that
            #   the file flushing takes some considerable time that I want to use for
            #   some other more interesting things :)
            #
            #self._file.flush()
            pass
            
    def setOptions( self, OptionList ):
        '''
        Sets the Options given on the OptionList to self. The options are the result of a user
        entering some data on a window that was constructed using the XML Options that was
        retrieved from the plugin using getOptions()
        
        This method MUST be implemented on every plugin. 
        
        @return: No value is returned.
        ''' 
        self.verbose = OptionList['verbose'].getValue()
        self._file_name = OptionList['fileName'].getValue()
        self._http_file_name = OptionList['httpFileName'].getValue()
        
        self._init()
    
    def getOptions( self ):
        '''
        @return: A list of option objects for this plugin.
        '''
        d1 = 'Enable if verbose output is needed'
        o1 = option('verbose', self.verbose, d1, 'boolean')
        
        d2 = 'File name where this plugin will write to'
        o2 = option('fileName', self._file_name, d2, 'string')
        
        d3 = 'File name where this plugin will write HTTP requests and responses'
        o3 = option('httpFileName', self._http_file_name, d3, 'string')
        
        ol = optionList()
        ol.add(o1)
        ol.add(o2)
        ol.add(o3)
        return ol

    def logHttp(self, request, response):
        '''
        log the http req / res to file.
        @parameter request: A fuzzable request object
        @parameter response: A httpResponse object
        '''
        now = time.localtime(time.time())
        the_time = time.strftime("%c", now)
        
        msg = '=' * 40 + 'Request ' + str(response.id) + ' - ' + the_time + '=' * 40 + '\n'
        self._write_to_HTTP_log(msg)
        self._write_to_HTTP_log(request.dump())
        msg2 = '\n' + '=' * 40 + 'Response ' + str(response.id) + ' - ' + the_time + '=' * 39 + '\n'
        self._write_to_HTTP_log(msg2)
        self._write_to_HTTP_log(response.dump())
        
        self._write_to_HTTP_log('\n' + '=' * (len(msg) - 1) + '\n')
        self._http.flush()

    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin writes the framework messages to a text file.
        
        Four configurable parameters exist:
            - fileName
            - httpFileName
            - verbose
        '''
