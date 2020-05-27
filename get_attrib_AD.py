#!python
#-*- coding: utf-8 -*-

#----------------------------------------------------------------------
# Description: Show statistic on Active Directory attributes 
# Author: Artyom Breus <Artyom.Breus@gmail.com>
# Created at: Thu Mar  7 08:04:30 UTC 2019
# Computer: HAB-HVP01.
# System: Linux 3.16.0-4-amd64 on x86_64
#
# Copyright (c) 2019 root  All rights reserved.
#
#----------------------------------------------------------------------


"""
/*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

###
#
# USAGE:  all_attrib2.py [AD_attribute1, AD_attribute2,....] [OU_1, OU_2]
#
###
"""

import ldap
import ldif
from time import sleep
from pprint import pprint
from sys import argv,stdout
import csv 
from output_func import html_table, print_table
import ad_user

# Configure section:
LDAP_HOST = '10.10.20.22'
LDAP_BASE_DN = 'OU=Khabarovsk,DC=my,DC=domain,DC=local'
BIND_USER = ad_user.simple + "@my.domain.local"
BIND_PASSWD = ad_user.simple_passwd         
#FILTER = '(objectCategory=person)'
#FILTER = 'cn=*'
#FILTER = '(objectClass=user)'
#FILTER = '(&(objectClass=user)(sAMAccountName=Breus*)(Enabled=True))'
FILTER = '(&(objectCategory=person)(displayName=*)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))'

def handle_ldap_entry(attributes,entry):
	res = []
	#return repr(entry)
	for attrib in attributes:
		r = entry.get(attrib,None)
		if r: r = r[0].decode('utf-8','replace')
		res.append(r)	                        
	return res

def statistic( data, first_row = False):
	res = [0] * len(data[0])
	for d in data:
		for idx in range( len(d) ):
			if d[idx]:
				res[idx] += 1
	#pprint(res)
	return res


def save_to_csv(filename, data = [[0]]):
	with open(filename + '.csv','w', newline='') as csvfile:
		rec = csv.writer(csvfile,dialect='excel',delimiter=';')
		rec.writerows(data)



def utf8_to_cp1251(data = [[0]]):
	res = []	
	for row in data:
		tmp = []		
		for cell in row:
			if type(cell) != str:
				tmp.append(cell)
			else:
				tmp.append(cell.encode('cp1251','ignore').decode('cp1251'))
		res.append( tmp )
	return res
			


def read_ldap(condition=FILTER, attributes=['cn',], base=LDAP_BASE_DN, handler=handle_ldap_entry):
	l = ldap.initialize('LDAP://' + LDAP_HOST)
	ldap.set_option(ldap.OPT_REFERRALS, 0)
	ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)	
	l.simple_bind_s(BIND_USER, BIND_PASSWD)
	#r = l.search_s(base,ldap.SCOPE_SUBTREE, condition, "*")
	r = l.search_s(base,ldap.SCOPE_SUBTREE, condition, attributes)
	res = []
	
	for dn,entry in r:
		res.append(handler(attributes,entry))
	l.unbind_s()
	return res

                                           

def main():

	if len(argv)>1:
		attr = argv[1].split(',')
		
		if len(argv)>2:
			sp_list = argv[2].split(',')
		else:
		        sp_list = ("Khabarovsk",)
			#sp_list = ("Khabarovsk","Ussurisk","Belogorsk")
			

	else:
		#attr = ['cn','displayname', 'department', 'manager', 'title', 'ipphone', 'office', 'officephone', 'telephoneNumber',	'Organization', 'physicalDeliveryOfficeName', 'MobilePhone','mobile' ]
		#attr = ['cn', 'department', 'title', 'mail','ipphone', 'office', 'officephone', 'telephoneNumber', 'organization', 'physicaldeliveryofficename', 'mobilephone','mobile','StreetAddress']
		#attr = ['cn','department','title','manager','mail','mobile','mobilephone']
		#attr = ['cn', 'company','department', 'title', 'ipPhone','telephoneNumber','ipPhone','mobile','mail']
		attr = ['cn', 'company','physicalDeliveryOfficeName','department', 'title', 'telephoneNumber','ipPhone','mobile','mail']
		#attr = ['officephone','mobilephone','SID']
		sp_list = ("Khabarovsk","Ussurisk","Belogorsk")
	
	#attr = [x.lower() for x in attr]

	for sp in sp_list:
		res = [ attr ]
		print("SP: " + sp)
		base = u"OU=%s,%s"%(sp,LDAP_BASE_DN)
		#base = LDAP_BASE_DN
		print(base + "\n\n")
		#tmp = read_ldap(FILTER, attr, base)
		tmp = read_ldap(FILTER, attr, base)
		res += tmp
		#return
		stat = statistic( tmp )
		#print("stat = %d, len = %d"%(stat[0],len(tmp)))
		res.append( [ "%.2f"%( x/len(tmp)*100 ) + " %" for x in stat ] )
		#pprint( res )
		res = utf8_to_cp1251(res)		
		open(sp + '.html','w').write(html_table(res, sp + " - процент заполнения атрибутов AD"))
		#open(sp + '.html','w').write(html_table(res, sp))
		save_to_csv(filename = sp, data = res[:-1])
		print(print_table(res))
		
                
if __name__ == '__main__':
	main()	
	

