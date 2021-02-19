# Log-orator
Handy decorator to simplify logging

![](https://media.giphy.com/media/2c3E1JNkOJ2Ba/giphy.gif)

## Usage ##
### Decorator
To use, simply decorate any desired method or function. Arguments must be named for decorator to work correctly.
```
@Log(message="this is the message before trying wrapped function", error="this is an error message", bye="this is a success message after function completes")
def im_wrapped():
    pass
```
#### 
If any arguments are missing, the default messages will be used.
```
@Log
def im_wrapped():
    pass
```

### Inline
To use inline, like a traditional logger, call class methods for the associated logging level

`Log.debug("message")`

`Log.info("message")`

`Log.warning("message")`

`Log.error("message")`

`Log.critical("message")`

### Adding loggers
Log class can be initialized before a wrapped function is called, or it will automatically create a log (using the path of the project) if setup isn't called beforehand. Additional calls to setup will create a new logger with the given name

`log_name = Log.add("LogName", "ApplicationName")`

`log_name = Log.add("DeveloperLog")`

`log_name = Log.add("UserLog", public=True)`

`log_name = Log.add()`



