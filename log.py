import logging
import inspect
import os
import sys
import datetime

class Log(object):
    """
    Logging class primarily used as a decorator
    """
    default_level = 20
    error_level = 50
    dev_logs = {}
    client_logs = {}
    app_name = None
    extra = {}

    @classmethod
    def add(cls, app_name=None, identifier=None, public=False, format_string=None, level=logging.DEBUG):
        """
        Sets logging location and initiates developer log, use in project root to automatically use project name
        as logging name

        :param app_name: Name of application you intend to log
        :param identifier: unique name of logger
        :param public: Will this log be a "public" log? (something catered to user view)
        :param format_string: logging format string
        :param level: the default level of the logger
        :return: logging object
        """
        if not app_name and not cls.app_name:
            # https://stackoverflow.com/a/59737458
            apth = os.path.abspath(__file__)
            ppth = os.environ['PYTHONPATH'].split(':')
            matches = [x for x in ppth if x in apth]
            root = min(matches, key=len)
            cls.app_name = apth.replace(root, "").split(os.path.sep)[0]
        else:
            cls.app_name = app_name
        if not identifier:
            identifier = str(datetime.datetime.now())
        if not public:
            name = "developer_" + identifier
        else:
            name = identifier

        logger = logging.getLogger(identifier)


        if format_string:
            formatter = logging.Formatter(format_string)


        if not public:
            cls.dev_logs[identifier] = logger
        else:
            cls.client_logs[identifier] = logger

        return logger


    def __init__(self, function=None, message=None, error=None, bye=None, extra={}, fatal=True, fatal_value=None,
                 default_level=None, error_level=None, loggers=[]):
        """

        :param function: wrapped function
        :type function: function or method
        :param message: custom message before a function is called
        :type message: string
        :param error: custom message after a function throws an exception
        :type error: string
        :param bye: custom message after a function completes without an exception
        :type bye: string
        :param fatal: should exception from wrapped function be re-raised after being caught?
        :type fatal: bool
        :param fatal_value: value to return if wrapped function throws exception and fatal is false
        :type fatal_value: any
        :param default_level: default logging level for this decorator call
        :type default_level: int
        :param error_level: default error logging level for this decorator call
        :type error_level: int
        :param loggers: names of loggers to use
        :type loggers: lisrt of strings
        """
        if hasattr(function, '__call__'):
            self.function = function
        self.message = message
        self.error = error
        self.bye = bye
        self.extra = extra or Log.extra
        self.fatal = fatal
        self.fatal_value = fatal_value
        if default_level in [0, 10, 20, 30, 40, 50]:
            self.default_level = default_level
        if error_level in [0, 10, 20, 30, 40, 50]:
            self.error_level = error_level
        self.loggers = loggers

    def __get__(self, obj, type_=None):
        """
        at runtime, takes wrapped function and sees if it is method or function, sends existing attributes
        to new instance

        @param obj:
        @type obj:

        @param type_:
        @type type_:

        @return:
        @rtype:
        """

        new = self.__class__(self.function.__get__(obj, type_))

        for attr in inspect.getargspec(Log.__init__).args[2:]:
            setattr(new, attr, getattr(self, attr))

        return new

    def __call__(self, *args, **kwargs):
        """
        Decorator does stuff before and after wrapped function depending on arguments in __init__

        @param args: args of wrapped function
        @type args: any

        @param kwargs: kwargs of wrapped function
        @type kwargs: any

        @return: any
        @rtype: any
        """

        # if the decorator was given arguments, the first argument on __call__ is the wrapped function
        if not hasattr(self, 'function'):
            self.function = args[0]
            return self

        dev_msg = "Trying : {} / {}".format(self.function.__module__, str(self.function))
        level = self.default_level

        if self.message:
            msg = self.message
            if not Log.client_logs:
                Log.add(public=True)
            if not self.loggers:
                for log in Log.client_logs.values():
                    log.log(level, msg, extra=self.extra)
            else:
                for log in self.loggers:
                    Log.client_logs[log].log(level, msg, extra=self.extra)

        if not Log.dev_logs:
            Log.add()
        if not self.loggers:
            for log in Log.dev_logs.values():
                log.log(level, dev_msg, extra=self.extra)
        else:
            for log in self.loggers:
                Log.dev_logs[log].log(level, dev_msg, extra=self.extra)

        error = False
        try:
            value = self.function(*args, **kwargs)
        except BaseException as exc:
            # get exc info
            exc_tup = sys.exc_info()
            exc_tup[2] = exc_tup[2].tb_next
            if self.fatal:
                raise
            else:
                value = self.fatal_value
        finally:
            if error:
                dev_msg = "** Error ** : {} / {}".format(self.function.__module__, str(self.function))
                msg = self.error or dev_msg
                level = self.error_level
                exc_info = exc_tup
            else:
                dev_msg = "Success : {} / {}".format(self.function.__module__, str(self.function))
                msg = self.bye or dev_msg
                level = self.default_level
                exc_info = False

            if self.message:
                if not self.loggers:
                    for log in Log.client_logs.values():
                        log.log(level, msg, extra=self.extra, exc_info=exc_info)
                else:
                    for log in self.loggers:
                        Log.client_logs[log].log(level, msg, extra=self.extra, exc_info=exc_info)
            if not self.loggers:
                for log in Log.dev_logs.values():
                    log.log(level, dev_msg, extra=self.extra, exc_info=exc_info)
            else:
                for log in self.loggers:
                    Log.dev_logs[log].log(level, dev_msg, extra=self.extra, exc_info=exc_info)
        return value

    @classmethod
    def inline(cls, message, public=False, extra={}, level=None, loggers=[]):
        level = level if level in [0, 10, 20, 30, 40, 50] else cls.default_level
        if public:
            if public is True:
                public = message
            if not Log.client_logs:
                Log.add(public=True)
            if not loggers:
                for log in Log.client_logs.values():
                    log.log(level, public, extra=extra or cls.extra)
            else:
                for log in loggers:
                    Log.client_logs[log].log(level, public, extra=extra or cls.extra)

        if not Log.dev_logs:
            Log.add()
        if not loggers:
            for log in Log.dev_logs.values():
                log.log(level, message, extra=extra or cls.extra)
        else:
            for log in loggers:
                Log.dev_logs[log].log(level, message, extra=extra or cls.extra)

    @classmethod
    def debug(cls, message, public=False, extra={}, loggers=[]):
        cls.inline(message, public, extra, 10, loggers)

    @classmethod
    def info(cls, message, public=False, extra={}, loggers=[]):
        cls.inline(message, public, extra, 20, loggers)

    @classmethod
    def warning(cls, message, public=False, extra={}, loggers=[]):
        cls.inline(message, public, extra, 30, loggers)

    @classmethod
    def error(cls, message, public=False, extra={}, loggers=[]):
        cls.inline(message, public, extra, 40, loggers)

    @classmethod
    def critical(cls, message, public=False, extra={}, loggers=[]):
        cls.inline(message, public, extra, 50, loggers)

