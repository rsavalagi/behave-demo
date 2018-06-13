import json
import jwt
import time
import hashlib
import requests
import datetime
from pprint import pprint
import xmltodict
import re
import sys
import platform
import random
import math
import os

# args $JENKINS_BUILD_NUM $ZEP_USER $ZEP_ACCESS_KEY $ZEP_SECRET_KEY


# USER
USER = 'admin'

# ACCESS KEY from navigation >> Tests >> API Keys
ACCESS_KEY = 'ZmQ2Nzk0OTktN2U3YS0zNWQ0LWIxYjgtM2I0MzBmM2FiNTdmIGFkbWluIFVTRVJfREVGQVVMVF9OQU1F'

# ACCESS KEY from navigation >> Tests >> API Keys
SECRET_KEY = 'wACKWxXWT9kYLS__bGU6K8aPiiUzEswscsq3MxL2X2Q'

# JWT EXPIRE how long token been to be active? 3600 == 1 hour
JWT_EXPIRE = 3600

# BASE URL for Zephyr for Jira Cloud
BASE_URL = 'https://prod-api.zephyr4jiracloud.com/connect'

pass_res = []
failed_res = []
unexecuted = []
final_result = {}


def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


class zephyr_integration:

    def __init__(self):
        pass

    # GENERATE TOKEN
    # token = jwt.encode(payload_token, SECRET_KEY, algorithm='HS256').strip().decode('utf-8')
    def create_token(self, rel_path):
        RELATIVE_PATH = rel_path
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        payload_token = {
            'sub': USER,
            'qsh': hashlib.sha256(CANONICAL_PATH.encode('utf-8')).hexdigest(),
            'iss': ACCESS_KEY,
            'exp': int(time.time()) + JWT_EXPIRE,
            'iat': int(time.time())
        }
        token = jwt.encode(payload_token, SECRET_KEY, algorithm='HS256').strip().decode('utf-8')
        return token

    def create_test_cycle(self, build_no=None):
        rel_path_for_test_cycle = '/public/rest/api/1.0/cycle'
        RELATIVE_PATH = rel_path_for_test_cycle
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        token = self.create_token(rel_path_for_test_cycle)
        headers = {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json',
            'zapiAccessKey': ACCESS_KEY
        }

        # creat the test cycle name:
        date = datetime.datetime.now()
        # test_cycle_name = 'rest_test_'+datetime.datetime.now().strftime('%M:%S.%f')[:-4]
        test_cycle_name = 'BVT-' + str(build_no) + ' ' + date.strftime("%D %H:%M")

        cycle = {
            'name': test_cycle_name,
            'projectId': 10000,
            'versionId': -1
        }

        # MAKE REQUEST:
        # raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)

            # PRINT RESPONSE: pretty print with 4 indent
            print(json.dumps(json_result, indent=4, sort_keys=True))
            print "------------------------------------------------"

            return json_result['cycleIndex'], json_result['name']

        else:
            print(raw_result.text)

    def add_tests_to_cycle(self, cycle_id):
        # cycleindex="0001505977226965-242ac112-0001"
        cycleindex = cycle_id
        rel_path_for_add_tests = '/public/rest/api/1.0/executions/add/cycle/%s' % (cycleindex)
        RELATIVE_PATH = rel_path_for_add_tests
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        token = self.create_token(rel_path_for_add_tests)
        headers = {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json',
            'zapiAccessKey': ACCESS_KEY
        }

        # creat the test cycle name:

        cycle = {"jql": "project = VRSC AND type = TEST AND LABELS = BVT", "versionId": -1, "projectId": 10000,
                 "method": "2"}

        # MAKE REQUEST:
        # raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)

            # PRINT RESPONSE: pretty print with 4 indent
            print(json.dumps(json_result, indent=4, sort_keys=True))
            print "------------------------------------------------"

        else:
            print(raw_result.text)

            # cycle = {"offset":0,"maxRecords":20,"fields":{},"zqlQuery":"project = \"VRSC\" AND fixVersion = \"Unscheduled\" AND cycleName = \"bvt\""}

    def get_all_execution_ids_and_testnames(self, testname):
        # cycleindex="0001505977226965-242ac112-0001"
        jql = "project = \"VRSC\" AND fixVersion = \"Unscheduled\" AND cycleName = \"%s\"" % (testname)
        RELATIVE_PATH = '/public/rest/api/1.0/zql/search'
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        token = self.create_token(RELATIVE_PATH)
        headers = {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json',
            'zapiAccessKey': ACCESS_KEY
        }
        cycle = {"offset": 0, "maxRecords": 50, "fields": {}, "zqlQuery": jql}
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):
            total = ''
            offset = ''

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)
            # pprint (json_result)
            print json_result.keys()
            total = json_result['totalCount']
            offset = json_result['currentOffset']
            print offset, total
            self.combine_offset_based_data(total, testname)
            # searh_obj = json_result['searchObjectList']
            # for each in searh_obj:
            #     # print  each['issueKey'],each ['issueSummary'] , "\t executionID:" + each['execution']['id']
            #     final_result[each['issueKey'].strip()] = each['execution']['id']

            # pprint(final_result)
            # print "------------------------------------------------"

        else:
            print(raw_result.text)

    def combine_offset_based_data(self, count, testname):
        jql = "project = \"VRSC\" AND fixVersion = \"Unscheduled\" AND cycleName = \"%s\"" % (testname)
        RELATIVE_PATH = '/public/rest/api/1.0/zql/search'
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        token = self.create_token(RELATIVE_PATH)
        headers = {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json',
            'zapiAccessKey': ACCESS_KEY
        }

        print "calculating the how many offsets present"
        float_data = count / 10.0
        offset = int(math.ceil(float_data))

        # Now for each offset send a post request and append the data so that all can be updated.
        global final_result

        for each in range(0, offset + 1):
            print "inside each"
            cycle = {"offset": each * 10, "maxRecords": 50, "fields": {}, "zqlQuery": jql}
            pprint(cycle)
            raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
            if is_json(raw_result.text):

                # JSON RESPONSE: convert response to JSON
                json_result = json.loads(raw_result.text)
                searh_obj = json_result['searchObjectList']
                for each in searh_obj:
                    # print  each['issueKey'],each ['issueSummary'] , "\t executionID:" + each['execution']['id']
                    final_result[each['issueKey'].strip()] = each['execution']['id']

        pprint(final_result)
        print "------------------------------------------------"

    def update_status_in_jira(self):
        RELATIVE_PATH = '/public/rest/api/1.0/executions'
        CANONICAL_PATH = 'POST&' + RELATIVE_PATH + '&'
        token = self.create_token(RELATIVE_PATH)
        headers = {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json',
            'zapiAccessKey': ACCESS_KEY
        }

        print "updating PASS status in jira"
        print pass_res
        cycle = {"executions": pass_res, "status": 1, "clearDefectMappingFlag": False, "testStepStatusChangeFlag": True,
                 "stepStatus": 1}
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)

            # PRINT RESPONSE: pretty print with 4 indent
            print(json.dumps(json_result, indent=4, sort_keys=True))

        else:
            print(raw_result.text)

        print "updating FAIL status in jira"
        print failed_res
        cycle = {"executions": failed_res, "status": 2, "clearDefectMappingFlag": False,
                 "testStepStatusChangeFlag": True, "stepStatus": 1}
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)

            # PRINT RESPONSE: pretty print with 4 indent
            print(json.dumps(json_result, indent=4, sort_keys=True))

        else:
            print(raw_result.text)

        print "updating UNEXECUTED status in jira"
        print unexecuted
        cycle = {"executions": unexecuted, "status": -1, "clearDefectMappingFlag": False,
                 "testStepStatusChangeFlag": True, "stepStatus": 1}
        raw_result = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=cycle)
        if is_json(raw_result.text):

            # JSON RESPONSE: convert response to JSON
            json_result = json.loads(raw_result.text)

            # PRINT RESPONSE: pretty print with 4 indent
            print(json.dumps(json_result, indent=4, sort_keys=True))

        else:
            print(raw_result.text)

            # Code from Raghu needs to be put here. for now use old jenkins junit.xml

    def read_junit_xml(self, local_container_path=None):
        print "reading the file from provided path"
        reports_path = 'reports'

        xml_files = os.listdir(reports_path)

        for xml in xml_files:
            local_container_path = os.path.join(reports_path, xml)
            with open(local_container_path, "rb") as f:  # notice the "rb" mode
                d = xmltodict.parse(f, xml_attribs=True)
                result_json = json.dumps(d, indent=4)

            test_data = json.loads(result_json)['testsuite']['testcase']

            failed = []
            passed = []
            result = {}

            for each in test_data:
                # result[each['@name']]= try: if each['failure']:   return 'FAIL'   else: return 'PASS'
                try:
                    if each['failure']:
                        result[each['@name'].strip()] = 'FAIL'
                except Exception as e:
                    result[each['@name'].strip()] = 'PASS'

            pprint(result)
            extracted_VRSC_val = {}

            for each in result.iterkeys():
                try:
                    match = re.search(r'^VRSC\-(\d){4}', each)
                    # print match.group()
                    extracted_VRSC_val[match.group()] = result[each]


                except AttributeError:
                    # print each
                    extracted_VRSC_val[each] = result[each]

            tests = {}
            execution_ids = final_result

            print "debug xml"
            print execution_ids

            for test in extracted_VRSC_val:
                tests[test] = extracted_VRSC_val[test]

            # with open("jira_output.txt", 'r') as infile:
            #     for line in infile:
            #         execution_ids[line.split(",")[0]] = line.split(",")[1].strip()
            # print "extension ids for tests" % tests

        def prepare_final_data(res):
            # pass_res=[]
            # failed_res = []
            # unexecuted = []

            for key, val in res.iteritems():
                if 'PASS' in val and len(val) == 2:
                    # print "pass id's"
                    pass_res.append(val[1])
                elif 'FAIL' in val and len(val) == 2:
                    # print "failed id's"
                    failed_res.append(val[1])
                elif len(val) == 1:
                    if not (val[0].isalnum()):
                        unexecuted.append(val[0])

                        # print  pass_res,failed_res,unexecuted
                        # print  failed_res,unexecuted

        def combineDictVal(*args):
            result = {}
            for dic in args:
                for key in (result.viewkeys() | dic.keys()):
                    if key in dic:
                        result.setdefault(key, []).append(dic[key])
            return result

        res = (combineDictVal(tests, execution_ids))
        print "res is %s" % (res)
        prepare_final_data(res)


if __name__ == '__main__':
    build_no = int(time.time())

    z = zephyr_integration()
    cycle_id, name = z.create_test_cycle(build_no)
    # name = 'BVT-138 10/05/17 18:48'
    # cycle_id = '0001507209531832-242ac112-0001'
    z.add_tests_to_cycle(cycle_id)
    z.get_all_execution_ids_and_testnames(name)
    z.read_junit_xml()
    z.update_status_in_jira()
