#! /usr/bin/env python3
# ^

######## Import ########
import os, sys, uuid, json, pwd, copy
from datetime import datetime

######## Functions ########
def json_dump (inp):
	return json.dumps(inp, sort_keys=True, indent=2)

def create_json_file (filename):
	handle = open (filename + '.json', "w")
	handle.write("{}")
	handle.close()

def read_json (filename):
	handle = open (filename + '.json', "r")
	content = json.loads(handle.read())
	handle.close()
	return content

def write_json_file (filename, content):
	handle = open (filename + '.json', "w")
	handle.write(json_dump(content))
	handle.close()

def print_help ():
	print ("Help for pyclitr\n")
	
	print("{:<20} {:<20} {:<35}".format("Command", "", "Description"))
	print("{:<20} {:<20} {:<35}".format("init", "", "Inititalize pyclitr for the current directory"))
	print("{:<20} {:<20} {:<35}".format("ls", "", "List all pending issues"))
	print("{:<20} {:<20} {:<35}".format("pending", "", "alias for ls"))
	print("{:<20} {:<20} {:<35}".format("completed", "", "List all completed issues"))
	print("{:<20} {:<20} {:<35}".format("add", "<>", "Adds a new issue with the given name. Additional values can be set, e.g. with project:test."))
	print("{:<20} {:<20} {:<35}".format("delete", "<uuid>", "Delete issue with specified uuid"))
	print("{:<20} {:<20} {:<35}".format("modify", "<uuid>", "Modify issue with specified uuid"))
	print("{:<20} {:<20} {:<35}".format("complete", "<uuid>", "Mark issue with specified uuid as completed"))
	

def note_edit (uuid, old, new):
	global pyclitr_dir
	edits = read_json(pyclitr_dir + 'edits')
	if not uuid in edits:
		edits[uuid] = []
	edits[uuid].append({'editor' : pwd.getpwuid(os.getuid()).pw_name, 'time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'from' : old, 'to' : new})
	
	write_json_file(pyclitr_dir + "edits", edits)

def dict_changes (first, second):
	for key, value in second.items():
		if key not in first:
			print ("Added " + key + str(value))
		elif value != first[key]:
			print ("Changed " + key + " from '" + str(first[key]) + "' to '" + str(value) + "'")

if True == False:
	if sys.argv[2] in issues:
		issue = issues[sys.argv[2]]
	else:
		status = 'completed'
		issues = read_json(pyclitr_dir + status)
		if sys.argv[2] in issues:
			issue = issues[sys.argv[2]]
		else:
			sys.exit("No item with this uuid has been found.")

# Set basic variables
cwd = os.getcwd() + '/'
pyclitr_dir = cwd + '.pyclitr/'

# Check if pyclitr has been initialized for this directory
if os.path.isdir (pyclitr_dir):
	initialized = True
else:
	initialized = False



if initialized == False:

	if not len(sys.argv) > 1:
		print ("Hidden directory .pyclitr does not exist. To set up pyclitr, use 'pyclitr init'\n\n")
		print_help()

	elif not sys.argv[1] == 'init':
		print ("Hidden directory .pyclitr does not exist. To set up pyclitr, use 'pyclitr init'\n\n")
		print_help()

elif len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'pending' or len(sys.argv) == 2 and sys.argv[1] == 'completed':
	
	if len(sys.argv) == 2 and sys.argv[1] == 'completed':
		issues = read_json(pyclitr_dir + "completed")
	else:
		issues = read_json(pyclitr_dir + "pending")

	order = ['entry', 'description', 'creator', 'project', 'uuid', 'assign', 'due']
	print("\033[4m{:<10}\033[0m \033[4m{:<45}\033[0m \033[4m{:<10}\033[0m \033[4m{:<15}\033[0m \033[4m{:<36}\033[0m \033[4m{:<10}\033[0m \033[4m{:<10}\033[0m".format(order[0], order[1], order[2], order[3], order[4], order[5], order[6]))
	for iuuid, issue in issues.items():
		print("{:<10} {:<45} {:<10} {:<15} {:<36} {:<10} {:<10}".format(issue[order[0]][0:10], issue[order[1]], issue[order[2]], issue[order[3]], iuuid, issue[order[5]], issue[order[6]]))

if len(sys.argv) == 2:

	if sys.argv[1] == 'init':

		os.mkdir (pyclitr_dir)
		open(pyclitr_dir + 'config', 'a').close()
		create_json_file (pyclitr_dir + 'pending')
		create_json_file (pyclitr_dir + 'completed')
		create_json_file (pyclitr_dir + 'edits')

		print ("Initialized at .pyclitr")

	elif sys.argv[1] == 'help':
		print_help()

if len(sys.argv) == 3 and sys.argv[1] == 'show':

	issues = read_json(pyclitr_dir + 'pending')

	if sys.argv[2] in issues:
		issue = issues[sys.argv[2]]
	else:
		issues = read_json(pyclitr_dir + 'completed')
		if sys.argv[2] in issues:
			issue = issues[sys.argv[2]]
		else:
			sys.exit("No item with this uuid has been found.")

	print("\033[4m{:<20}\033[0m \033[4m{:<35}\033[0m".format("Name", "Value"))
	print("{:<20} {:<35}".format("UUID", sys.argv[2]))
	for key, value in issue.items():
		if key != 'annotation' and value != '': 
			print("{:<20} {:<35}".format(key, value))

	# Display edits if there are any
	edits = read_json (pyclitr_dir + "edits")
	if sys.argv[2] in edits:
		for i in edits[sys.argv[2]]:
			print ("\n\033[1m" + i['editor'] + "\033[0m edited this task on \033[4m" + i['time'] + "\033[0m:")

			dict_changes (i['from'], i['to'])

if len(sys.argv) > 2 and sys.argv[1] == 'add':

	pending = read_json(pyclitr_dir + 'pending')
	iuuid = str(uuid.uuid1())

	issue = {"entry" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "creator" : pwd.getpwuid(os.getuid()).pw_name, 'annotation' : [], 'project' : '', 'status' : 'pending', 'assign' : '', 'due' : ''}

	args = sys.argv[2:]

	title = ''
	for i in args:
		attr = i.split(":")
		if (len(attr) == 2):		
			issue[str(attr[0])] = str(attr[1])
		else:
			title = title + i + " "
	issue['description'] = str(title).strip(" ")

	pending[iuuid] = issue
	write_json_file (pyclitr_dir + "pending", pending)
	print ("Issue \033[1m" + title + "\033[0m added")

if len(sys.argv) > 2 and sys.argv[1] == 'modify':

	# Check whether this issue is pending or completed
	status = 'pending'
	issues = read_json(pyclitr_dir + status)

	if sys.argv[2] in issues:
		issue = issues[sys.argv[2]]
	else:
		status = 'completed'
		issues = read_json(pyclitr_dir + status)
		if sys.argv[2] in issues:
			issue = issues[sys.argv[2]]
		else:
			sys.exit("No item with this uuid has been found.")

	original = copy.copy(issue)

	args = sys.argv[3:]
	title = ''
	for i in args:
		attr = i.split(":")
		if (len(attr) == 2):
			issue[str(attr[0])] = str(attr[1])
		else:
			title = title + i + " "
	if title != '':
		issue['description'] = str(title).strip(" ")

	issues[sys.argv[2]] = issue
	write_json_file (pyclitr_dir + status, issues)
	print ("Issue \033[1m" + sys.argv[2] + " (" + issue['description'] + ")" + "\033[0m modified")

	note_edit(sys.argv[2], original, issue)

if len(sys.argv) > 2 and sys.argv[1] == 'complete':

	# Check whether this issue is pending or completed
	status = 'pending'
	issues = read_json(pyclitr_dir + status)

	if sys.argv[2] in issues:
		issue = issues[sys.argv[2]]
	else:
		status = 'completed'
		issues = read_json(pyclitr_dir + status)
		if sys.argv[2] in issues:
			issue = issues[sys.argv[2]]
		else:
			sys.exit("No item with this uuid has been found.")

	original = copy.copy(issue)

	issue['status'] = 'completed'

	completed = read_json(pyclitr_dir + "completed")
	completed[sys.argv[2]] = issue
	write_json_file (pyclitr_dir + "completed", completed)

	del issues[sys.argv[2]]
	write_json_file (pyclitr_dir + status, issues)
	print ("Issue \033[1m" + sys.argv[2] + " (" + issue['description'] + ")" + "\033[0m moved to completed")

	note_edit(sys.argv[2], original, issue)

if len(sys.argv) == 3 and sys.argv[1] == 'delete':

	# Check whether this issue is pending or completed
	status = 'pending'
	issues = read_json(pyclitr_dir + status)

	if sys.argv[2] in issues:
		issue = issues[sys.argv[2]]
	else:
		status = 'completed'
		issues = read_json(pyclitr_dir + status)
		if sys.argv[2] in issues:
			issue = issues[sys.argv[2]]
		else:
			sys.exit("No item with this uuid has been found.")

	del issues[sys.argv[2]]

	write_json_file (pyclitr_dir + status, issues)

