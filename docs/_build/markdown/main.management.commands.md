# main.management.commands package

## Submodules

## main.management.commands.runapscheduler module


### class main.management.commands.runapscheduler.Command(stdout=None, stderr=None, no_color=False, force_color=False)
Bases: `django.core.management.base.BaseCommand`


#### handle(\*args, \*\*options)
The actual logic of the command. Subclasses must implement
this method.


#### help( = 'Runs apscheduler.')

### main.management.commands.runapscheduler.delete_old_job_executions(max_age=604800)
This job deletes all apscheduler job executions older than max_age from the database.

## Module contents
