The purpose of this project is to create a wrapper around timewarrior (The linux command timew) in order to make the CLI more readable. The project will be written in python and use python fire for argument parsing. The command will be called "clock" and the options will behave the same way as timewarrior 

For example, `clock s :month` will call `timew s :month` under the hood.

The major change I want from timewarrior is to display all times in 12-hour format instead of 24-hour format

Additionally, I want a new command `clock begin <tags> "<annotation>"` that calles `timew start <tags>` and then `timew ann "<annotation>"`

Right now, the main commands I want overhauled with a nicer "TUI" look and 12h format are `day`, `week`, `month` and `summary :week, :month, :yesterday` etc

The other commands can simply be passed to timew

In your develepment, feel free to consult `timew help` and try commands. Also, feel free to test the python script yourself, I have backed up my timewarrior data.


