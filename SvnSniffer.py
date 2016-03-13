import sys, os, subprocess, xml.dom.minidom, pprint

class LogEntry:
	def __init__(self, revision, author, message):
		self.revision = revision
		self.author = author
		self.message = message
		
	def __str__(self):
		return "Rev {} by '{}' with message: {}".format(self.revision, self.author, self.message)

svn_path = sys.argv[1]
search_items_file = sys.argv[2]
svn_username = sys.argv[3]

output = subprocess.Popen(["svn", "log", "--xml", "-g", "--username="+svn_username, svn_path], stdout=subprocess.PIPE).communicate()[0]

document = xml.dom.minidom.parseString(output.strip())
log_xml_entries = document.documentElement.getElementsByTagName("logentry")
logs = []
for entry in log_xml_entries:
	revision = entry.getAttribute("revision")
	author = entry.getElementsByTagName("author")[0].firstChild.nodeValue
	message = entry.getElementsByTagName("msg")[0].firstChild.nodeValue
	logs.append(LogEntry(revision, author, message))

search_items = []
with open(search_items_file, 'r') as file:
	search_items = [item.strip() for item in file.readlines()]

def containsSearchItem(log):
	hits = []
	for item in search_items:
		print("Checking if {} is in {}".format(item, log.message))
		if (item in log.message):
			hits.append(item)
	return hits
						
results = [(containsSearchItem(log), log) for log in logs]
results = [(search_item, log) for search_item, log in results if search_item]

print("\n")
print("--- Revision search trace ---")
for result in results:
	search_item, log = result
	print ("{} was found in revision {} commited by '{}'".format(search_item, log.revision, log.author))
print("\n")

print("--- Items status ---")
if not results:
	print("Nothing was found")
	exit()
else:
	found_search_items, found_log_items = zip(*results)

max_length_str = str(max(len(s) for s in search_items))
for item in search_items:
	status = None
	flat_list = [item for sublist in found_search_items for item in sublist]
	if (item in flat_list): 
		status = "Ok"		
	else:
		status = "Bad"
	print("{:{width}} - {}".format(item, status, width=max_length_str))	
