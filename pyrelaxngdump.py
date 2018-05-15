#!/usr/bin/python3

from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import os.path
from json import dumps
from copy import deepcopy

indentsize=5

def dump_attributes(element, ns):
	attributes=''
	attribs=element.findall(".//ns:attribute", ns)
	for attrib in attribs:
		attributes+=' ' + attrib.attrib['name'] + "="

	return attributes

def dump_element(root, ns, indent, element, name, parents):
	#print("Dumping: '" + element + " - parents: " + dumps(parents))
	#print("*** " + element + " ***")
	newparents = deepcopy(parents)

	indentstr=" " * indent * indentsize
	subindentstr=indentstr+(' ' * indentsize)
	definenode=root.find("ns:define[@name='"+element+"']", ns)
	elementnode=definenode.find("ns:element", ns)
	if elementnode:
		if name:
			displayname=name
		else:
			displayname=elementnode.attrib['name']

		print(indentstr+"<" + displayname + dump_attributes(elementnode, ns) + ">")
		if element in parents:
			print(subindentstr+" - skipping " + element)
		else:
			newparents.append(element)

			subelements=elementnode.findall(".//ns:element", ns)
			for subelement in subelements:
				print(subindentstr + "<" + subelement.attrib['name'] + " />")

			subclasses=elementnode.findall(".//ns:ref", ns)
			for subclass in subclasses:
				parent=subclass.find("..")
				if parent and parent.tag == "element":
					elementname=parent.attrib['name']
				else:
					elementname=None

				dump_element(root, ns, indent+1, subclass.attrib['name'], elementname, newparents)

#			members=elementnode.findall("./ns:zeroOrMore/ns:ref", ns)
#			for member in members:
#				dump_element(root, ns, indent+1, member.attrib['name'], newparents)

		print(indentstr+"</" + displayname + ">")
	else:
		print(indentstr+"<" + element + " />")


parser = ArgumentParser()
parser.add_argument("-r", "--relax-schema", help="Relax schema file to dump")
parser.add_argument("-i", "--ignore-file", help="File containing a list of element names to hide")

args = parser.parse_args()

if args.relax_schema:
	if os.path.isfile(args.relax_schema):
		tree = ET.parse(args.relax_schema)
		root = tree.getroot()

		ns = {'ns': 'http://relaxng.org/ns/structure/1.0'};

		start = root.find("ns:start", ns)
		startref = start.find("ns:ref", ns)
		parents=[]
		dump_element(root, ns, 0, startref.attrib['name'], None, parents)
	else:
		print('Error opening relax schema file: \'' + args.relax_schema + '\'')
		exit(-2)

else:
	parser.print_help()
	exit(-1)

