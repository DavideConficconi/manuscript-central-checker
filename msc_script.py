from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import argparse
import json

import traceback

from time import sleep

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def query_website(driver, url, username, password, timeout):

	driver.get(url)

	try:
		element_present = EC.presence_of_element_located((By.NAME, "USERID"))
		WebDriverWait(driver, timeout).until(element_present)
		login_bar = driver.find_element_by_name("USERID")
		login_bar.clear()
		login_bar.send_keys(username)
		pass_bar = driver.find_element_by_name("PASSWORD")
		pass_bar.clear()
		pass_bar.send_keys(password)
		pass_bar.send_keys(Keys.RETURN)
	except TimeoutException:
		print("Timed out waiting for page %s to load" % url)
		exit()

	sleep(timeout)

	nav_links = driver.find_elements_by_class_name("nav-link")
	for i in nav_links:
		if(i.text == "Author"):
			i.click()
			break
	
	try:
		element_present = EC.presence_of_element_located((By.ID, "authorDashboardQueue"))
		WebDriverWait(driver, timeout).until(element_present)
		author_table = driver.find_element_by_id("authorDashboardQueue")
		queue_id=0
		while(True):
			try:
				current_queue="queue_"+str(queue_id)
				queue_bar = author_table.find_element_by_id(current_queue)
				infos = queue_bar.find_elements_by_tag_name("td")

				infos_len = len(infos)
				adm_found = False
				adm_index = -1
				for c, i in enumerate(infos):
					if not adm_found:
						adms = [j.strip() for j in i.text.split("\n") if "ADM:" in j or "INF:" in j or "EIC:" in j]
						if len(adms) > 0:
							data = "\n".join(adms)
							adm_found = True
							adm_index = c
						else:
							data = ""
					elif c - adm_index == 2:
						data = bcolors.FAIL + i.text.strip() + bcolors.ENDC
					elif c < infos_len - 2:
						data = i.text.strip()
					elif c < infos_len - 1:
						continue
					else:
						data = "Submitted on: " + i.text.strip()
					if data != "":
						print(data)

				print("\n\n")
				queue_id += 1
			except NoSuchElementException:
				break
	except TimeoutException:
		print("Timed out waiting for author page to load")
		exit()


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-j", "--json", type=str, required=True, \
		help="a json file containing the list of websites to check along with username and password")
	parser.add_argument("-t", "--timeout", type=int, default=2, \
		help="[optional] timeout waiting for website response (default=2)")
	args = parser.parse_args()
	json_file_name = args.json

	try:
		options = Options()
		options.add_argument("--headless")
		driver = webdriver.Chrome('./chromedriver', options=options)

		print("\n\n")

		with open(json_file_name) as json_file:
			data = json.load(json_file)
			for k in data.keys():
				print(bcolors.WARNING + "-----------------Querying %s----------------\n\n\n" % (k) + bcolors.ENDC)
				url = data[k][0]["url"]
				username = data[k][0]["username"]
				password = data[k][0]["password"]
				query_website(driver, url, username, password, args.timeout)

	except Exception: 
		traceback.print_exc()
	finally:
		driver.close()


if __name__ == '__main__':
	main()

