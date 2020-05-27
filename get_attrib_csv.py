#!python
#-*- coding: utf8 -*-


from sys import argv,exit
from time import sleep
import csv

from pprint import pprint


def open_file(filename):	               
	data = []
	user_data = {}
	header = None
	with open(filename, 'r', encoding='cp1251', errors="strict") as csvfile:
		filereader = csv.reader(csvfile, dialect='excel', delimiter=';', quoting=csv.QUOTE_NONE)		
		for row in filereader:
			print(row)
			if not header:
				header = row
				continue
			user_data = {}			
			for idx in range(header.__len__()):
				user_data[header[idx]] = row[idx] #[ row[idx].encode('utf-8') ]
			data.append(user_data)		
		pprint(data)
	return data


def main():
	if len(argv) > 1:
		filled_csv  = argv[1]
	else:
		print("USAGE: read_attrib <OU-named-filled.csv>")
		exit(1)                     

	data = open_file(filled_csv)
	

if __name__ == '__main__':
	main()

