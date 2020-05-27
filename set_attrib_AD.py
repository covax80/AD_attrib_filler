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
# USAGE:  set_attrib.py get_attr.export.csv
#
###
"""


import ldap
import ldap.modlist as modlist

from pprint import pprint
from get_attrib_csv import open_file
from sys import argv, exit, exc_info
from time import sleep

import ad_user

#MODE = 'SAFE'
MODE = 'UNSAFE'
LDAP_HOST = '10.10.0.22'
LDAP_BASE_DN = 'OU=Khabarovsk,DC=my,DC=domain,DC=local'
BIND_USER = ad_user.admin + "@my.domain.local"
BIND_PASSWD = ad_user.admin_passwd

def setup_ldap_connection():
	ldap.set_option(ldap.OPT_REFERRALS, 0)
	ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 2)
	l = ldap.initialize('LDAP://' + LDAP_HOST)
	ldap.set_option(ldap.OPT_REFERRALS, 0)
	l.simple_bind_s(BIND_USER, BIND_PASSWD)
	return l	


def parent(dn):
	return ",".join(dn.split(',')[1:])

def attr_filled(ad,ou,cn,attr):
	#print("\nattr: " + attr)
	filter = "(cn=%s*)"%cn
	try:	
		res = ad.search_s(ou,ldap.SCOPE_SUBTREE,'(&(objectCategory=person)' + filter + ')',[attr,])		
		#print("1")
		#pprint(res)
		new_dn = ""		
		for dn,entry in res:
			new_dn = dn
			res = entry
			break
		if res == []:
			print("Пустое поле [] вместо {}")
			res = {}
		rec_possible = (not bool(res))	
	
	except (ldap.NO_SUCH_OBJECT,ldap.FILTER_ERROR):
		print("Unexpected error:", exc_info()[0])
		# Ошибка появляется либо из-за некорретно отредактированного CSV, либо неверного DN (_OU)
		#res, rec_possible = attr_filled(parent(dn),dn,attr)
		return (ou, 'Error', True )
	return new_dn, res, rec_possible
	           
def record_data_AD( data =[], ad_ou_name = None):	
	ad = setup_ldap_connection()		
	ou ="OU=%s,"%ad_ou_name + LDAP_BASE_DN    
	dn =""
	old_value = None	
	for user in data:
		try:
			dn = "cn=%s,"%user['cn'] + ou
		except KeyError:
			print("ERROR: В файле CSV используются \",\" а далжны использоваться \";\" в качестве разделителей")
			print(user)
			exit(1)		

		print("Редактирование \t\t[ %s ]"%user['cn'])
		for csv_attr,csv_value in user.items():
			logprint = "\nMode=%s:%s:%s: "%(MODE,user['cn'],csv_attr)
			rec_possible = False
			old_value = None
			if csv_attr.lower() == 'cn':
				continue
			dn, old_value, rec_possible = attr_filled(ad,ou,user['cn'],csv_attr)
			if MODE == 'SAFE':
				if not rec_possible:
					print(logprint + 'Уже есть значение')
					continue					
			if (MODE == 'UNSAFE') or rec_possible:
				if old_value == 'Error':
					print(logprint + 'Не найден человек из CSV файла в AD. Пропускаем')
					continue
				if old_value == {}:
					print(logprint + 'Запись в пустое поле')
					old_value = { csv_attr: [ None ] }

				if csv_value == '':
					print(logprint + 'Запись None')
					new_value = { csv_attr: [ None ] }
					#continue 
				else:
					new_value = { csv_attr: [ csv_value.encode('utf-8') ] }
				print("\noldvalue = %s \nnewvalue = %s\n\n"%(old_value, new_value))
				if new_value == old_value:
					print(logprint  + "Cтарое значение равно новому")
					continue
				print(logprint  + 'REC')
				ldif = modlist.modifyModlist(old_value, new_value)
				
				#pprint(dn)
				try:
					#sleep(0.2)
					ad.modify_s(dn, ldif)
					print(logprint  + 'REC \t\t\t\t[ OK ]')
				except (ldap.CONSTRAINT_VIOLATION,ldap.UNWILLING_TO_PERFORM):
					print(logprint  + 'REC \t\t\t\t[ FAIL ] \n',"Error:", exc_info()[0])
		                                
	ad.unbind_s()
	return 0


def main():
	
	if len(argv) > 1:
		filled_csv  = argv[1]
	else:
		print("USAGE: read_attrib <OU-named-filled.csv>")
		exit(1)

	data = open_file( filled_csv )
	if data:
		ad_ou_name = filled_csv[:-4]		
		err_id = record_data_AD( data, ad_ou_name )
	exit(err_id)


                
if __name__ == '__main__':
	main()	
	

