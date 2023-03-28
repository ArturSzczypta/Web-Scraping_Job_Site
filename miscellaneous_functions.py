''' Extracting already downloaded data to text files'''
import json
import ast
import re
from collections import Counter

def extracting_to_files(file_name):
    keys = ['req_expected', 'req_optional', 'resp_bullets', 'tech_expected', 'tech_optional']

    # Open the input and output files
    with open(file_name, 'r', encoding='utf-8') as input_file:
        with open('req_expected.txt', 'w', encoding='utf-8') as req_expected_file, \
             open('req_optional.txt', 'w', encoding='utf-8') as req_optional_file:

            # Loop through each lline with JSON
            for line in input_file:
                # Load the JSON object
                obj = json.loads(line)

                # Write the values for the desired keys to their respective output files
                req_expected_file.write(str(obj.get('req_expected', '')) + '\n')
                req_optional_file.write(str(obj.get('req_optional', '')) + '\n')


def extract_tech_without_repetition(file_with_lists,file_with_tech):
    tech_set = set()
    sorted_tech = []
    # Open the file with the list of technologies/languages
    with open(file_with_lists, 'r', encoding='utf-8') as file:
        
        for line in file:
            line.strip()
            if line == 'None':
                continue
            tech_list = ast.literal_eval(line)
            if tech_list is not None:
                tech_set.update(tech_list)
        
    sorted_tech = sorted(tech_set)

    # Open a file to write the unique technologies/languages to
    with open(file_with_tech, 'a', encoding='utf-8') as output_file:

        for item in sorted_tech:
            output_file.write(item + '\n')

def update_tech(file_with_tech, new_tech_set=None):
    ''' Add new technologies/languages and then sort'''
    # Extract technologies/languages to a set
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file:
        for line in file:
            tech_set.add(line.strip())
    
    # Add new technologies/languages if provided
    if new_tech_set is not None:
        tech_set.update(new_tech_set)

    # Sort and write unique technologies/languages to file
    sorted_tech = sorted(tech_set)
    with open(file_with_tech, 'w', encoding='utf-8') as file:
        for item in sorted_tech:
            file.write(item + '\n')

def removing_salary_nulls(file_with_jsons, new_file_with_jsons):
    ''' Remove salary keys if there is no salary'''
    # define the keys to delete
    keys_to_delete = ['salary_from', 'salary_to', 'salary_currency', 'salary_long_form']

    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            
            # check if the condition is met (e.g. a different key has value False)
            if json_obj.get('is_salary') == False:
                # delete the keys to delete from the JSON object
                for key in keys_to_delete:
                    if key in json_obj:
                        del json_obj[key]
            
            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def nest_current_listings(file_with_jsons, new_file_with_jsons):
    ''' Nest salary and technology keys'''
    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            
            # Store salary data in nested dictionary, remove is_salary boolean
            if json_obj.get('is_salary') == True:
                json_obj['salary'] = {
                'salary_from': json_obj.pop('salary_from'),
                'salary_to': json_obj.pop('salary_to'),
                'salary_currency': json_obj.pop('salary_currency'),
                'salary_long_form': json_obj.pop('salary_long_form')
                }
                del json_obj['is_salary']
            if json_obj.get('is_salary') == False:
                del json_obj['is_salary']

            if json_obj.get('tech_expected') == True:
                # Store tech data in nested dictionary
                json_obj['technologies'] = {
                'expected': json_obj.pop('tech_expected'),
                'optional': json_obj.pop('tech_optional')
                }

            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def replace_descriptions(file_name_1, file_name_2):
    lines = None
    with open(file_name_1, 'r', encoding='utf-8') as file_1:
        lines = file_1.readlines()

    with open(file_name_2, 'w',encoding='utf-8') as file_2:
        for line in lines:
            line = line.replace('salary_from','min')
            line = line.replace('salary_to','max')
            line = line.replace('salary_currency','currency')
            line = line.replace('salary_long_form','pay_period')
            file_2.write(line)


def nest_current_listings(file_with_jsons, new_file_with_jsons):
    ''' Nest salary and technology keys'''
    # open the input file and output file
    with open(file_with_jsons, 'r',encoding='utf-8') as input_file,\
    open(new_file_with_jsons, 'w',encoding='utf-8') as output_file:
        # iterate over each line in the input file
        for line in input_file:
            # parse the JSON object from the line
            json_obj = json.loads(line)
            '''
            # Store salary data in nested dictionary, remove is_salary boolean
            if json_obj.get('is_salary') == True:
                json_obj['salary'] = {
                'salary_from': json_obj.pop('salary_from'),
                'salary_to': json_obj.pop('salary_to'),
                'salary_currency': json_obj.pop('salary_currency'),
                'salary_long_form': json_obj.pop('salary_long_form')
                }
                del json_obj['is_salary']
            if json_obj.get('is_salary') == False:
                del json_obj['is_salary']
            '''
            
            # Store tech data in nested dictionary
            json_obj['requirements'] = {
            'expected': json_obj.pop('req_expected'),
            'optional': json_obj.pop('req_optional')
            }

            # write the modified JSON object to the output file
            output_file.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def skill_patterns(skill_set):
    ''' Create regex pattern for given skill set
    I assume names of languages and technologies names shorter than 3
    have to be search as \b%s\b (R, C)
    Longer names can be part of longer string (PostgreSQL, MySQL for sql)
    Each pattern dinds all instances of upper/lower case and capitalised'''

    skills_schort = []
    skills_long = []
    for skill in skill_set:
        if len(skill) <3:
            skills_schort.append(re.escape(skill))
        else:
            skills_long.append(re.escape(skill))

    pattern_1 = None
    pattern_2 = None
    if len(skills_schort) > 0:
        pattern_1 = '|'.join(skills_schort)
    if len(skills_long) > 0:
        pattern_2 = '|'.join(skills_long)

    if pattern_1 and pattern_2:
        pattern = re.compile(r'\b(%s)\b|(%s)' % (pattern_1, pattern_2),
            re.IGNORECASE)
    elif pattern_1:
        pattern = re.compile(pattern_1, re.IGNORECASE)
    elif pattern_2:
        pattern = re.compile(pattern_2, re.IGNORECASE)
    else:
        pattern = ''

    return pattern

def check_for_skill_set(substring, skill_set):
    ''' Check for elements of skill set in the substring
    Cancel pipeline if none of skills is mentioned'''
    return re.search(skill_patterns(skill_set),substring, flags=re.IGNORECASE)

def update_file(old_urls_file, urls_file):
    ''' Adds new records, removes old ones'''
    old_records = set()
    with open(old_urls_file, 'r',encoding='utf-8') as file:
        old_records = set(line.strip() for line in file)

    with open(urls_file, 'r+',encoding='utf-8') as file:
        todays_links = set(line.strip() for line in file)
        new_records = todays_links - old_records
        print(f'New: {len(new_records)}')
        # Clear out the content of the file
        file.seek(0)
        file.truncate()
        # Write new urls
        for url in new_records:
            file.write(url + '\n')


def filter_unused_tech(file_with_tech, file_with_listings, file_only_used_tech):
    ''' Keep only technologies/languages found in the scraped listings'''
    # Extract technologies/languages to a set
    tech_set = set()
    filtered_tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file_1:
        for line in file_1:
            tech_set.add(line.strip())
    
    with open(file_with_listings, 'r', encoding='utf-8') as file_2:
        count = 0
        for line in file_2:
            for tech in tech_set:
                tech_escaped = re.escape(tech)
                pattern = re.compile(r'\b(%s)\b' % tech_escaped, re.IGNORECASE)
                if pattern.search(line):
                    filtered_tech_set.add(tech)
            count += 1
            if count % 10 == 0:
                print(count)

    # Sort and write unique found technologies/languages to file
    sorted_tech = sorted(filtered_tech_set)
    with open(file_only_used_tech, 'w', encoding='utf-8') as file:
        for item in sorted_tech:
            file.write(item + '\n')


def extract_all_tech(file_with_tech, file_with_listings, new_file_with_listings):
    ''' Extract all technologies/languages/annrevations saved in a file
    Add them to given dictionary as a list'''
    # Save requirements to set
    tech_set = set()
    with open(file_with_tech, 'r', encoding='utf-8') as file_1:
        for line in file_1:
            tech_set.add(line.strip())
    
    # Open each line as string. After extraction convert to dictionary.
    all_tech_found = []
    with open(file_with_listings, 'r', encoding='utf-8') as file_2,\
    open(new_file_with_listings, 'a', encoding='utf-8') as file_3:
        count = 0
        for line in file_2:
            line = line.strip()
            tech_found = []
            for tech in tech_set:
                tech_escaped = re.escape(tech)
                pattern = re.compile(r'\b(%s)\b' % tech_escaped,re.IGNORECASE)
                if pattern.search(line):
                    tech_found.append(tech)
                    all_tech_found.append(tech)

            tech_found.sort()
            new_dict = json.loads(line)
            new_dict['technologies']['scraped'] = tech_found

            file_3.write(json.dumps(new_dict, ensure_ascii=False) + '\n')
    # Count and print
    counter = Counter(all_tech_found)
    sorted_values = counter.most_common()
    print(sorted_values)

#extract_all_tech('technologies_scraped.txt','new_listings_scraped.txt', 'new_new_listings_scraped.txt')

def simplify_dev_practices(file_with_listings, new_file_with_listings):
    ''' Replace each dictionary in list with just main value'''
    
    with open(file_with_listings, 'r', encoding='utf-8') as file_2,\
    open(new_file_with_listings, 'a', encoding='utf-8') as file_3:
        count = 0
        for line in file_2:
            line = line.strip()
            new_dict = json.loads(line)
            if new_dict['dev_practices'] != None:
                my_list = new_dict['dev_practices']
                new_list = [element['primaryTargetSiteName'] for element in my_list]
                new_dict['dev_practices'] = new_list

                print(new_dict['url'], new_dict['dev_practices'])

            file_3.write(json.dumps(new_dict, ensure_ascii=False) + '\n')


#Skills_freq_list = [('SQL', 3188), ('Python', 1518), ('English', 1262), ('Java', 1100), ('Git', 976), ('Azure', 938), ('Rest', 874), ('Cloud', 837), ('DevOps', 835), ('Linux', 792), ('C', 764), ('Microsoft', 753),('Integration', 748), ('Docker', 731), ('Scrum', 702), ('CI', 685), ('Agile', 680), ('testy', 654), ('Oracle', 638),('JavaScript', 612), ('Teams', 601), ('API', 587), ('Kubernetes', 576), ('CD', 572), ('AWS', 564), ('CI CD', 561), ('Jira', 543),('BI', 495), ('MS SQL', 483), ('UML', 430), ('Jenkins', 428), ('Continuous Integration', 428), ('Bash', 427), ('NET', 423), ('Architecture', 415), ('SQL Server', 409), ('Google', 395), ('ERP', 390),('Automation', 385), ('Kafka', 381), ('BPMN', 377), ('Excel', 374), ('CSS', 358), ('ETL', 353), ('Power BI', 348), ('Spring', 344), ('PostgreSQL', 342),('R', 338), ('Core', 331), ('Office', 314), ('Confluence', 313), ('SOAP', 309), ('Databases', 302), ('GCP', 302), ('PL SQL', 299), ('Angielski', 298),('Enterprise Architect', 296),('REST API', 295), ('Ansible', 291), ('HTML', 283), ('Postman', 281), ('PowerShell', 279), ('Jest', 279), ('SAP', 278), ('Azure DevOps', 276), ('Continuous Deployment', 262), ('Scripting', 261),('MySQL', 261), ('Selenium', 259), ('Google Cloud', 255),('Microsoft Azure', 254), ('React', 252), ('PHP', 237), ('Big Data', 230), ('Maven', 226), ('Spring Boot', 220), ('Spark', 218), ('Angular', 208), ('Apache', 206), ('Windows Server', 202),('XML', 198), ('JS', 198), ('Machine Learning', 196), ('Bazy Danych', 193), ('DDD', 193), ('UI', 192), ('T-SQL', 192), ('Google Cloud Platform', 185), ('Network', 183), ('Solid', 183),('SOLID', 183), ('Microsoft SQL', 180), ('Visual Studio', 176), ('Tableau', 172), ('Terraform', 172), ('SoapUI', 172), ('Hibernate', 169), ('.js', 168), ('Microsoft SQL Server', 167), ('noSQL', 167),('NoSQL', 167), ('CAN', 166), ('MS Office', 166), ('VMWare', 158), ('VBA', 155), ('ITIL', 152),('GitLab', 152), ('MongoDB', 152), ('UX', 149), ('.NET', 148), ('TDD', 147), ('Native', 147), ('Data Science', 145), ('Active Directory', 142), ('Consulting', 142), ('MVC', 140),('OpenShift', 139), ('Access', 136), ('MS SQL Server', 136), ('ASP.NET', 135), ('ElasticSearch', 134), ('Storage', 132), ('MS Excel', 129), ('RabbitMQ', 127),('HTML5', 127), ('Design Patterns', 127), ('Splunk', 125), ('Microservices', 125), ('Spring Framework', 125), ('Data Warehouse', 124), ('Scala', 123), ('Web Services', 122),('Statistics', 121), ('Android', 121), ('MSSQL', 119), ('Hadoop', 118), ('Version control', 118), ('AI', 115), ('Data Analytics', 114), ('SAS', 113), ('ISTQB', 112), ('IP', 109),('Unix', 108), ('UNIX', 108), ('unix', 108), ('Grafana', 108), ('OOP', 108), ('JSON', 107), ('DataBricks', 106), ('Databricks', 106), ('Relational databases', 106), ('Typescript', 105), ('TypeScript', 105), ('GitHub', 104),('ELK', 100), ('Project Management', 99), ('GraphQL', 99), ('BDD', 98), ('JMeter', 98), ('jMeter', 98), ('Jmeter', 98), ('CRM', 97), ('GET', 96), ('LAN', 95), ('Symfony', 94), ('Snowflake', 93), ('Inne', 93),('Entity Framework', 92), ('AD', 91), ('Structure', 91), ('QA', 90), ('SVN', 89), ('Junit', 88), ('JUnit', 88), ('jUnit', 88), ('TCP', 87), ('Embedded', 85), ('Microsoft Excel', 84), ('REST Assured', 84), ('Rest Assured', 84),('Airflow', 84), ('TCP IP', 82), ('Workflow', 82), ('React.js', 82), ('jQuery', 82), ('JQuery', 82), ('Data analysis', 81), ('Go', 80), ('Scratch', 79), ('Google Analytics', 79), ('networking', 79), ('Networking', 79),('Redis', 78), ('Apache Spark', 78), ('Groovy', 77), ('Prometheus', 77), ('CASE', 77), ('Certyfikat ISTQB', 77), ('PowerBi', 76), ('PowerBI', 76), ('Continuous Delivery', 76), ('Bash Python', 75), ('Cloud solutions', 75),('SharePoint', 74), ('WAN', 74), ('Cloud Services', 74), ('Unity', 74), ('Data Factory', 73), ('Kanban', 73), ('kanban', 73), ('Android Studio', 73), ('CentOS', 72), ('SLA', 72), ('Java 8', 72), ('Shell', 70), ('NAS', 70),('Gatling', 70), ('Kali Linux', 70), ('Minecraft', 70), ('Unity 3D', 70), ('BitBucket', 69), ('Comarch ERP', 69), ('Swagger', 69), ('Jira Confluence', 69), ('JIRA Confluence', 69), ('Optima', 67), ('ISO', 67), ('UX UI', 67),('togaf', 67), ('Perl', 66), ('Azure SQL', 66), ('Business Analysis', 66), ('CSS3', 66), ('IntelliJ', 66), ('OS', 65), ('Networks', 65), ('Gradle', 65), ('unit testing', 65), ('Unit Testing', 65), ('technical support', 64),('Qlik', 64), ('ASP.NET MVC', 64), ('Node.js', 64), ('SIEM', 64), ('RPA', 63), ('SSIS', 63), ('ServiceNow', 62), ('Servicenow', 62), ('User Stories', 62), ('BigQuery', 62), ('Azure Cloud', 61), ('Batch', 61),('web applications', 61), ('Serverless', 61), ('IIS', 60), ('Ubuntu', 60), ('Puppet', 60), ('Power Query', 60), ('power query', 60), ('Webservices', 60), ('WebServices', 60), ('WEBSERVICES', 60), ('Version Control System', 60),('DevExpress', 60), ('HANA', 59), ('Power Point', 59), ('Containers', 59), ('Containerization', 59), ('enova365', 59), ('Scripting languages', 58), ('hyper-v', 58), ('Hyper-V', 58), ('VPN', 58), ('nginx', 58), ('Nginx', 58),('NGINX', 58), ('UAT', 58), ('ORM', 58), ('Adobe', 58), ('dns', 57), ('DNS', 57), ('Cisco', 57), ('SalesForce', 57), ('Microsoft Dynamics', 56), ('Cassandra', 56),('Bootstrap', 56), ('bootstrap', 56), ('Apache Airflow', 56), ('Agile SCRUM', 55), ('Kibana', 54), ('AJAX', 54), ('Data modeling', 54), ('Cypress', 54), ('LeSS', 53), ('LESS', 53), ('firewall', 53), ('Firewall', 53), ('ESB', 53),('ETL ELT', 53), ('Debugging', 52), ('Reporting Services', 52), ('Enterprise Architekt', 52), ('Web API', 51), ('IDEA', 51), ('Pyspark', 51), ('pyspark', 51), ('pySpark', 51), ('PySpark', 51), ('Hive', 51), ('Debian', 50),('PL-SQL', 50), ('Data Architecture', 50), ('Data architecture', 50), ('WinForms', 50), ('Network Security', 50), ('Data Governance', 49), ('Java 11', 49), ('WPF', 49), ('MS-SQL', 48), ('Foundation', 48), ('Amazon Web Services', 48),('ELK Stack', 48), ('CI CD Azure DevOps', 48), ('OpenStack', 47), ('Qlik Sense', 47), ('Azure Data Factory', 46), ('Django', 46), ('TFS', 46), ('TeamCity', 45), ('Informatica', 45), ('Authorization', 45), ('Red Hat', 44),('WebLogic', 44), ('Weblogic', 44), ('WEBLOGIC', 44), ('Microsoft Power BI', 44), ('TensorFlow', 44), ('Tensorflow', 44), ('HTML CSS', 44), ('SAP BW', 44), ('Pandas', 44), ('WCF', 44), ('JPA', 44), ('PLSQL', 43),('BPM', 43), ('VLAN', 43), ('WMS', 43), ('Dax', 43), ('DAX', 43), ('Magento', 43), ('Redux', 43), ('ASP.NET Core', 43), ('ASP.Net Core', 43), ('Asp.Net Core', 43), ('.NET Core', 43), ('DWH', 42), ('HP', 42),('MS Windows', 42), ('SOA', 42), ('Vue', 42), ('Scrum methodology', 42), ('SpringBoot', 42), ('Springboot', 42), ('MariaDB', 41), ('PyTorch', 41), ('Waterfall', 41), ('Combine', 41), ('GitFlow', 41),('Gitflow', 41), ('sccm', 40), ('SCCM', 40), ('XSLT', 40), ('Synapse', 40), ('Graylog', 40), ('CMS', 40), ('4GL', 40), ('NLP', 40), ('SAFe', 40), ('ADF', 40), ('React Native', 40), ('Microsoft Windows', 39),('KVM', 39), ('Atlassian', 39), ('SAAS', 39), ('SaaS', 39), ('Saas', 39), ('Software testing', 39), ('TSQL', 39), ('Oracle SQL', 38), ('iOS', 38), ('Data Studio', 38), ('UIPath', 38), ('XPath', 38),('Celonis', 38), ('OWASP', 38), ('Tomcat', 37), ('TOMCAT', 37), ('RedHat', 37), ('Fortinet', 37), ('IaC', 37), ('Vault', 37), ('Webcon', 37), ('PMI', 37), ('GCC', 37), ('gcc', 37), ('IoT', 37), ('Selenium WebDriver', 37),('Selenium Webdriver', 37), ('artifactory', 36), ('Artifactory', 36), ('Forms', 36), ('backup', 36), ('Postgres', 36), ('SQL NoSQL', 36), ('Shiny', 36), ('Power Automate', 36), ('Archimate', 36), ('Cloud Platforms', 36),('Microservices Architecture', 36), ('WebService', 36), ('High Availability', 35), ('OLAP', 35), ('DB2', 35), ('Mongo', 35), ('Cybersecurity', 34), ('cybersecurity', 34), ('CyberSecurity', 34), ('Artificial Intelligence', 34),('RESTful', 34), ('Microsoft Office', 34), ('Next', 33), ('HA', 33), ('Zabbix', 33), ('APEX', 33), ('Apex', 33), ('VB', 33), ('JMS', 33), ('NeoLoad', 33), ('Disaster Recovery', 32), ('Windows Linux', 32), ('MS Azure', 32),('FIORI', 32), ('Fiori', 32), ('MES', 32), ('Dash', 32), ('Gerrit', 32), ('Kinesis', 32), ('Hbase', 32), ('HBase', 32), ('REST APIs', 32), ('Github Actions', 32), ('GitHub Actions', 32), ('NightWatch', 32), ('Exchange', 31),('Internet', 31), ('Ruby', 31), ('Google Data Studio', 31), ('Low-Code', 31), ('Shell Scripting', 31), ('Teradata', 31), ('Logs', 31), ('Infrastructure as Code', 31), ('CQRS', 31), ('HTTP', 30), ('ROBOT', 30), ('Bamboo', 30),('Office 365', 30), ('NiFi', 30), ('Helm', 30), ('Lambda', 30), ('JAVA EE', 30), ('Java EE', 30), ('Activity', 29), ('IDS', 29), ('Automotive', 29), ('Qlikview', 29), ('Test Driven Development', 28), ('DELL', 28), ('Dell', 28),('dhcp', 28), ('DHCP', 28), ('Firewalls', 28), ('SEO', 28), ('Oracle DB', 28), ('Express', 28), ('Mockito', 28), ('Jasmine', 28), ('React Redux', 28), ('5G', 27), ('GPO', 27), ('Integration Services', 27), ('Camunda', 27),('UI UX', 27), ('SSRS', 27), ('Apache Flink', 27), ('Robot Framework', 27), ('Cloudera', 27), ('Jee', 27), ('RAN', 26), ('NIST', 26), ('Flask', 26), ('PaaS', 26), ('PAAS', 26), ('Laravel', 26), ('Spark Streaming', 26),('Unix Linux', 25), ('UNIX LINUX', 25), ('M365', 25), ('Dynamics AX', 25), ('Consul', 25), ('Ferryt', 25), ('Kotlin', 25), ('Vue.js', 25), ('SAS 4GL', 25), ('Sas 4GL', 25), ('Kanban methodology', 25), ('Webcon BPS', 25),('IAM', 24), ('vSphere', 24), ('ActiveMQ', 24), ('Wirtualizacja', 24), ('wirtualizacja', 24), ('SAP BASIS', 24), ('AML', 24), ('NumPy', 24), ('Microsoft .NET', 24), ('Crystal Reports', 23), ('Satellite', 23),('Visio', 23), ('WSDL', 23), ('SIT', 23), ('JSP', 23), ('Eclipse', 23), ('IDE', 23), ('Mikroserwisy', 23), ('Scikit-Learn', 23), ('scikit-learn', 23), ('DLP', 23), ('Metadata Management', 23), ('Pytest', 23), ('pytest', 23),('PyTest', 23), ('NuGet', 23), ('Blazor', 23), ('AWS Cloud', 22), ('Routing', 22), ('routing', 22), ('Golang', 22), ('IPSec', 22), ('IPSEC', 22), ('Linux Server', 22), ('Microsoft Windows Server', 22), ('Apache Kafka', 22),('apache kafka', 22), ('SDLC', 22), ('Snowflake Data Cloud', 22), ('AWS Kinesis', 22), ('Python 3', 22), ('SRE', 22), ('ISO 27001', 22), ('Karma', 22), ('Cucumber', 22), ('HPE', 21), ('k8s', 21), ('K8s', 21), ('SWARM', 21),('ABAP', 21), ('Rancher', 21), ('Elastic Search', 21), ('Architecture design', 21), ('Ms Project', 21), ('MS Project', 21), ('Chef', 21), ('DynamoDB', 21), ('Dataflow', 21), ('DataFlow', 21), ('Mulesoft', 21), ('MuleSoft', 21), ('Adobe Analytics', 21), ('Confluent', 21), ('Elastic Stack', 21), ('MS Dynamics 365', 21), ('Pimcore', 21), ('PHP 7.x', 21), ('WebSocket', 21), ('Websocket', 21), ('Miro', 21), ('SQL PLSQL', 21), ('MQ', 20), ('S 4 HANA', 20), ('Stream Analytics', 20), ('ITSM', 20), ('PM', 20), ('monitoring tools', 20), ('Monitoring tools', 20), ('Microservice Architecture', 20), ('Sonarqube', 20), ('SonarQube', 20), ('Pig', 20), ('TENABLE', 20), ('IBM InfoSphere', 20), ('SVM', 20), ('Delphi', 20), ('Flux', 20), ('Hortonworks', 20), ('JIRA Confluence Tool Suite', 20), ('Panaya', 20), ('ITIL principles', 20), ('Routers', 20), ('systemy ERP', 20), ('RHEL', 19), ('Solr', 19), ('SSO', 19), ('SCOM', 19), ('Qlickview', 19), ('Flutter', 19), ('RWD', 19), ('Deep Learning', 19), ('Domain Driven Design', 19), ('MS Dynamics AX', 19), ('Foundry', 19), ('Data mesh', 19), ('McAfee', 19), ('Mcafee', 19), ('Embedded C', 19), ('SAP HANA', 19), ('STL', 19), ('Comptia', 19), ('WebAPI', 19), ('WebApi', 19), ('Xamarin', 19), ('Oauth', 19), ('SAP ECC', 19), ('Figma', 19), ('SAP S 4 HANA', 18), ('Symantec', 18), ('restore', 18), ('Java Script', 18), ('SAP ERP', 18), ('AI ML', 18), ('Angielski B2', 18), ('relacyjne bazy danych', 18), ('Relacyjne bazy danych', 18), ('Composer', 18), ('Computer Vision', 18), ('Xray', 18), ('Observability', 18), ('Scrum Kanban', 18), ('WSO2', 18), ('Grails', 18), ('Cucumber.js', 18), ('TestLink', 18), ('Testlink', 18), ('SQL Profiler', 18), ('Firebase', 18), ('Adobe Experience Manager', 18), ('DRY', 18), ('Magnolia', 18), ('SonarCube', 18), ('Instana', 18), ('Spinnaker', 18), ('Test Suite', 18), ('Practitioner', 18), ('Comptia Security', 18), ('UX Research', 18), ('AWK', 17), ('WLAN', 17), ('MLOps', 17), ('UML 2', 17), ('Prince 2', 17), ('Power Apps', 17), ('Big Query', 17), ('Scrumban', 17), ('Ivanti', 17), ('Virtual Machines', 17), ('Clang', 17), ('PrimeFaces', 17), ('Drupal', 17), ('Subversion', 17), ('Karate', 17), ('Burp', 17), ('Microsoft 365', 16), ('Service Desk', 16), ('Unifi', 16), ('LDAP', 16), ('DBPlus', 16), ('Redgate', 16), ('SCRUM 3', 16), ('BPMN 3', 16), ('Miscroservices 2', 16), ('Analytics 4', 16), ('Azure DevOps 2', 16), ('S3', 16), ('CheckPoint', 16), ('Checkpoint', 16), ('ASP.NET Core MVC', 16), ('Behavior Driven Development', 16), ('ECMAScript', 16), ('SAP Hybris', 16), ('Unix shell', 16), ('Amplitude', 16), ('Research Tools', 16), ('Spring-Webflow', 16), ('SAP Fiori', 16), ('Palo alto', 16), ('Palo Alto', 16), ('GEB', 16), ('Burp suite', 16), ('ZAP', 16), ('Logistic Regression', 16), ('Gradient Boosting', 16), ('SAN', 15), ('IPS', 15), ('Oracle BI', 15), ('Looker', 15), ('cryptography', 15), ('RDBMS', 15), ('CloudFormation', 15), ('Azure Synapse', 15), ('Dataproc', 15), ('Azure GCP', 15), ('German language', 15), ('FortiGate', 14), ('Fortigate', 14), ('BigData', 14), ('Ethernet', 14), ('SCADA', 14), ('FastAPI', 14), ('Fastapi', 14), ('PyCharm', 14), ('TIA', 14), ('Excel VBA', 13), ('JBOSS', 13), ('Jboss', 13), ('JBoss', 13), ('Dynatrace', 13), ('BI Tools', 13), ('Power Pivot', 13), ('RedShift', 13), ('Redshift', 13), ('Azure Databricks', 13), ('LTE', 13), ('Pub Sub', 13), ('Security tools', 13), ('webpack', 13), ('EDI', 13), ('Apache Tomcat', 12), ('Insight', 12), ('Windows Serwer', 12), ('VM', 12), ('MS Windows Server', 12), ('SAP Business Objects', 12), ('Google Tag Manager', 12), ('Sass', 12), ('NGRX', 12), ('SASS', 12), ('NgRx', 12), ('Collibra', 12), ('Power Platform', 12), ('Cyberbezpieczeństwo', 12), ('Arm', 12), ('ARM', 12), ('Angular.js', 12), ('Embedded Systems', 12), ('Keras', 12), ('MacOS', 12), ('ETL tools', 12), ('ETL Tools', 12), ('Python 3.x', 12), ('SCSS', 12), ('GtiLab', 12), ('Office365', 11), ('PKI', 11), ('Informatica PowerCenter', 11), ('PowerCenter', 11), ('HAProxy', 11), ('IaaC', 11), ('Product Management', 11), ('Lean', 11), ('Websockets', 11), ('EC2', 11), ('Functional Testing', 11), ('RDS', 11), ('MATLAB', 11), ('npm', 11), ('NPM', 11), ('Black', 11), ('RxJS', 11), ('Rxjs', 11), ('RXJS', 11), ('J2EE', 11), ('Telecommunication', 10), ('CCNA', 10), ('CISSP', 10), ('MS Access', 10), ('ASM', 10), ('VoIP', 10), ('Veeam', 10), ('MLflow', 10), ('MLFlow', 10), ('YAML', 10), ('VS', 10), ('Azure AD', 10), ('Entity Framework Core', 10), ('PHPUnit', 10), ('SSAS', 10), ('PRINCE2', 10), ('Prince2', 10), ('GKE', 10), ('Alteryx', 10), ('Sonar', 10), ('Oracle Apex', 10), ('Microsoft Power Automate', 10), ('Prophet', 9), ('Enterprise Manager', 9), ('Microsoft IIS', 9), ('Firebird', 9), ('Oracle WebLogic', 9), ('Oracle Weblogic', 9), ('Windows 10', 9), ('Remedy', 9), ('BGP', 9), ('WiFi', 9), ('FTP', 9), ('COM', 9), ('Com', 9), ('Cosmos DB', 9), ('PowerQuery', 9), ('IaaS', 9), ('Polski', 9), ('Angular 2', 9), ('Datadog', 9), ('DataDog', 9), ('Event Hub', 9), ('Integration testing', 9), ('NodeJS', 9), ('ETL design', 9), ('Data Visualization tools', 9), ('Nexus', 9), ('CircleCI', 9), ('Amazon AWS', 9), ('GIS', 9), ('RestAPI', 9), ('SoC', 9), ('SOC', 9), ('SQL Management Studio', 9), ('API Testing', 9), ('LUA', 9), ('Lua', 9), ('SAP Business One', 8), ('Data Guard', 8), ('VCS', 8), ('Proxmox', 8), ('EDR', 8), ('QT', 8), ('Qt', 8), ('PLC', 8), ('Ant', 8), ('CMake', 8), ('Cmake', 8), ('LINQ', 8), ('NHibernate', 8), ('MQTT', 8), ('Matplotlib', 8), ('O365', 8), ('Message Broker', 8), ('Switch', 8), ('NestJS', 8), ('EMC', 8), ('switching', 8), ('OpenCV', 8), ('Windows Service', 8), ('Języki programowania', 8), ('SAP ABAP', 8), ('Atlas', 8), ('Exchange Online', 8), ('Platformy Azure', 8), ('Sitecore CMS', 8), ('CISM', 7), ('JVM', 7), ('IPC', 7), ('Mikrotik', 7), ('Nagios', 7), ('SSMS', 7), ('PLM', 7), ('BluePrism', 7), ('Rust', 7), ('Control-M', 7), ('websphere', 7), ('WebSphere', 7), ('Websphere', 7), ('ML AI', 7), ('Natural Language Processing', 7), ('SNS', 7), ('EntityFramework', 7), ('manual testing', 7), ('Manual testing', 7), ('GDPR', 7), ('Apache Beam', 7), ('wsus', 7), ('WSUS', 7), ('Microsoft Technologies', 7), ('Impala', 7), ('Cloud Storage', 7), ('Random Forest', 7), ('XGBoost', 7), ('Ab initio', 7), ('GSM', 7), ('Ruby on Rails', 7), ('Jenkins Pipelines', 7), ('Azure Active Directory', 7), ('MDM', 7), ('IDS IPS', 7), ('UI Design', 7), ('Oracle Data Integrato', 7), ('AngularJS', 7), ('SOAR', 7), ('Console App', 7), ('Django Rest Framework', 7), ('ISTQB Foundation Level', 7), ('Microsoft365', 7), ('Pakiet Microsoft Office', 7), ('Google Workspace', 6), ('F5', 6), ('AV', 6), ('microsoft server', 6), ('VDI', 6), ('PL pgSQL', 6), ('AIX', 6), ('AppDynamics', 6), ('FW', 6), ('Postfix', 6), ('Atlassian Jira', 6), ('Atlassian JIRA', 6), ('S 4Hana', 6), ('VBS', 6), ('CCNP', 6), ('Oracle Linux', 6), ('ERP OPTIMA', 6), ('UTM', 6), ('PCI DSS', 6), ('Knime', 6), ('KNIME', 6), ('SAS Visual Analytics', 6), ('SQL Server Reporting Services', 6), ('RedMine', 6), ('Redmine', 6), ('Viya', 6), ('VB.NET', 6), ('HMI', 6), ('AWS Glue', 6), ('ECS', 6), ('CloudWatch', 6), ('BPMS', 6), ('Azure Synapse Analytics', 6), ('Synapse Analytics', 6), ('SDK', 6), ('Microsoft Azure DevOps', 6), ('Boost', 6), ('Gtest', 6), ('Concourse', 6), ('Slack', 6), ('CANoe', 6), ('Azure Cognitive Services', 6), ('Aurora', 6), ('VBScript', 6), ('CDK', 6), ('OSS', 6), ('PAM', 6), ('CEH', 6), ('S4 Hana', 6), ('S4 HANA', 6), ('FPGA', 6), ('UMTS', 6), ('Swift', 6), ('Windows Server administration', 6), ('Streamsoft', 6), ('TestNG', 6), ('Regression Testing', 6), ('HFM', 6), ('Travis CI', 6), ('Visual Studio 2022', 6), ('Ranger', 6), ('IBM MQ', 5), ('Linux OS', 5), ('RMAN', 5), ('MS Teams', 5), ('WAF', 5), ('Networker', 5), ('Ubiquiti', 5), ('Citrix', 5), ('HashiCorp', 5), ('SFTP', 5), ('Google BigQuery', 5), ('PWA', 5), ('Spring MVC', 5), ('AutoCAD', 5), ('AUTOSAR', 5), ('Helm Charts', 5), ('Gherkin', 5), ('Microsoft BI Stack', 5), ('Microsoft SSIS', 5), ('Odata', 5), ('Oozie', 5), ('PMP', 5), ('Embedded Linux', 5), ('SAST', 5), ('DAST', 5), ('Acceptance testing', 5), ('CSV', 5), ('AIM', 5), ('Microsoft O365', 5), ('SAS Enterprise Guide', 5), ('Success Factors', 5), ('Unit Test', 5), ('Network Protocols', 5), ('Packer', 5), ('RESTful API', 5), ('Visual Studio Code', 5), ('SQS', 5), ('ADO', 5), ('OKTA', 5), ('CCTV', 5), ('Graphana', 5), ('IMS', 5), ('Nordic', 5), ('Clean Architecture', 5), ('ASP.NET Web Forms', 5), ('Zend', 5), ('WordPress', 5), ('OneDrive', 5), ('DFS', 5), ('Dell EMC', 5), ('Appium', 5), ('ES6', 5), ('Celery', 5), ('Automation Anywhere', 5), ('FileNet', 5), ('Solidity', 5), ('IFRS17', 4), ('Solvency II', 4), ('Jiry', 4), ('Rozwiązania chmurowe', 4), ('snmp', 4), ('Terminal', 4), ('Service Now', 4), ('AutomateNow', 4), ('AutomateNOW', 4), ('NFS', 4), ('nfs', 4), ('Docker-compose', 4), ('Openssl', 4), ('Hashicorp Vault', 4), ('MS Power Point', 4), ('Tableu', 4), ('XLM', 4), ('Modbus', 4), ('SQL Server Integration Services', 4), ('MS Power BI', 4), ('API Gateway', 4), ('Liquibase', 4), ('MPLS', 4), ('Commvault', 4), ('ISO27001', 4), ('EMR', 4), ('Visual Studio 2019', 4), ('Control M', 4), ('Azure Pipelines', 4), ('OLAP Cubes', 4), ('ELT Integration', 4), ('Microsoft Power Platform', 4), ('Java or C', 4), ('SageMaker', 4), ('Amazon SageMaker', 4), ('Team Management', 4), ('gRPC', 4), ('Cobol', 4), ('COBOL', 4), ('Databricks Structured Streaming', 4), ('Azure Stream Analytics', 4), ('Datafactory', 4), ('SQLite', 4), ('Microservices patterns', 4), ('Cloud SQL', 4), ('GCS', 4), ('CNN', 4), ('RNN', 4), ('ECR', 4), ('Nomad', 4), ('Octopus Deploy', 4), ('PowerApps', 4), ('BERT', 4), ('Google Optimize', 4), ('Yocto', 4), ('Zephyr', 4), ('xUNIT', 4), ('XUnit', 4), ('xUnit', 4), ('NUnit', 4), ('ASPICE', 4), ('QNAP', 4), ('HTML 5', 4), ('VHDL', 4), ('SAP PI PO', 4), ('Network Administration', 4), ('Microsoft Office 365', 4), ('MS Dynamics 365 CRM', 4), ('Oracle Forms', 4), ('NLTK', 4), ('Magento 2', 4), ('CIS', 4), ('EPM', 4), ('HP LoadRunner', 4), ('SignalR', 4), ('Zookeeper', 4), ('Google Cloud Storage', 4), ('NATS', 4), ('Sqlalchemy', 4), ('SqlAlchemy', 4), ('SQLAlchemy', 4), ('SAP SD', 4), ('SAP S4 HANA', 4), ('Azure AI', 4), ('SAML', 4), ('Essbase Smartview', 4), ('CDC', 4), ('VSC', 4), ('unit integration testing', 4), ('Behavior-Driven Development', 4), ('Wireshark', 4), ('IPv4', 3), ('Lenovo', 3), ('webMethods', 3), ('Microsoft Windows Serwer', 3), ('NAT', 3), ('Juniper', 3), ('x86', 3), ('SIP', 3), ('RADIUS', 3), ('Radius', 3), ('OSPF', 3), ('Dovecot', 3), ('Linux Centos', 3), ('Varnish', 3), ('Red Hat Linux', 3), ('NGFW', 3), ('SQL Server Analysis Services', 3), ('Sparx Enterprise Architect', 3), ('MS PowerPoint', 3), ('SQL DB2', 3), ('Dart', 3), ('OpenAPI', 3), ('Servlets', 3), ('MVP', 3), ('Canvas', 3), ('Advanced Excel', 3), ('MSSQL Server', 3), ('Autodesk', 3), ('SEP', 3), ('ITIL Incident', 3), ('Avaloq Core Platform', 3), ('ARM Templates', 3), ('Docker Swarm', 3), ('Angular 8', 3), ('Six', 3), ('Power BI Desktop', 3), ('Linux Kernel', 3), ('LoRa', 3), ('XSL', 3), ('Google Kubernetes Engine', 3), ('Cloud Dataproc', 3), ('VPC', 3), ('Pyhton', 3), ('CloudOps', 3), ('Mainframe', 3), ('Simulink', 3), ('Malware', 3), ('Regex', 3), ('WAS', 3), ('SPARQL', 3), ('Storm', 3), ('SuperSet', 3), ('Test-Driven Development', 3), ('SciPy', 3), ('App Service', 3), ('Java SpringBoot', 3), ('RobotFramework', 3), ('InTune', 3), ('Intune', 3), ('inTune', 3), ('Adobe Target', 3), ('Tealium Tag Manager', 3), ('FreeRTOS', 3), ('GoogleTest', 3), ('RTOS', 3), ('JDE', 3), ('APS', 3), ('Gulp', 3), ('WebFlux', 3), ('Seaborn', 3), ('Extreme', 3), ('Assembly', 3), ('Java SE', 3), ('FLEXERA', 3), ('Flexera', 3), ('GAMP', 3), ('Arduino', 3), ('Objective-C', 3), ('Security protocols', 3), ('Outlook', 3), ('Spring Cloud', 3), ('API REST SOAP', 3), ('Continous Integration Delivery', 3), ('Spring Security', 3), ('JBoss Application Ser', 3), ('Jasper Reports', 3), ('PHP 7 8', 3), ('NLU', 3), ('Cloud BigTable', 3), ('MVVM', 3), ('Transfer Learning', 3), ('SPSS', 3), ('ASP.NET Web API', 3), ('Agility', 3), ('Umbraco', 3), ('Performance Test', 3), ('Twig', 3), ('CAD', 3), ('Signavio', 3), ('SAP FICO', 3), ('AMQP', 3), ('network automation', 3), ('DRF', 3), ('Automation testing', 3), ('Automation Testing', 3), ('JavaScript ES6', 3), ('AI Platform', 3), ('Google Cloud AI Platform', 3), ('Google Design Sprints', 3), ('LDAP Services', 3), ('Windows Defender', 3), ('No SQL', 3), ('ASP.NET Core SignalR', 3), ('XHTML', 3), ('NewRelic', 3), ('CloudFront', 3), ('Cloudfront', 3), ('Route53', 3), ('Content Hub', 3), ('Zendesk', 2), ('AI Robotics', 2), ('Integration Test', 2), ('4G', 2), ('CCSP', 2), ('IFRS4', 2), ('EndPoint Manager', 2), ('PEGA', 2), ('ScriptRunner', 2), ('ESET', 2), ('Windows Active Directory', 2), ('Logstash', 2), ('WebRTC', 2), ('Call Center', 2), ('Aruba', 2), ('GNU Linux', 2), ('Windows Powershell', 2), ('XDR', 2), ('MS SQL Windows', 2), ('Microsoft Hyper-V', 2), ('PgAdmin', 2), ('Draw.io', 2), ('IREB', 2), ('ADONIS', 2), ('MS Visio', 2), ('Postresql', 2), ('InfluxDB', 2), ('API Management', 2), ('IBM WebSphere', 2), ('ETL Informatica', 2), ('Stress testing', 2), ('ATP', 2), ('Allure', 2), ('ISMS', 2), ('AWS EMR', 2), ('Angular JS', 2), ('Azure Monitor', 2), ('Asana', 2), ('UX Design', 2), ('Google Suite', 2), ('Pentaho', 2), ('3GPP', 2), ('Yang', 2), ('FORTRAN', 2), ('Vim', 2), ('PQL', 2), ('Azure Data Pipelines', 2), ('Lakehouse', 2), ('AWS EKS', 2), ('Kubeflow', 2), ('Microsoft Dynamics Certification', 2), ('Jupyter Notebook', 2), ('LightGBM', 2), ('Jamf', 2), ('OpenSearch', 2), ('ArgoCD', 2), ('Istio', 2), ('SQL Oracle databases', 2), ('Ansible Tower', 2), ('Windows OS', 2), ('CKAD', 2), ('PIWIK', 2), ('BLE', 2), ('Bare-metal', 2), ('Buildroot', 2), ('MISRA', 2), ('Imperva', 2), ('ksh', 2), ('Next.js', 2), ('React Angular', 2), ('JPA Hibernate', 2), ('DICOM', 2), ('Tailwind', 2), ('System Testing', 2), ('System testing', 2), ('Altium', 2), ('Windchill', 2), ('SSWiN', 2), ('S4 HANA SAP', 2), ('Verilog', 2), ('Modelsim', 2), ('Natural Language Understanding', 2), ('Caffe', 2), ('MMSC', 2), ('SMSC', 2), ('LabView', 2), ('IP MPLS', 2), ('MDG', 2), ('RFC', 2), ('qTest', 2), ('Security Tests', 2), ('ZHS', 2), ('EDI OTM', 2), ('VBA JAVA', 2), ('Ionic', 2), ('SQL relational databases', 2), ('MS SQL Oracle Database', 2), ('Java Core', 2), ('Monday', 2), ('SQL Server 2019', 2), ('GitOPS', 2), ('Xamarin Maui', 2), ('QGIS', 2), ('FME', 2), ('Tableau development', 2), ('TeamViewer', 2), ('NLP NLU', 2), ('Formal Grammars', 2), ('LMS', 2), ('KISS', 2), ('analiza przestrzenna', 2), ('PostGIS', 2), ('x86 Power', 2), ('OKD', 2), ('Mercurial', 2), ('mercurial', 2), ('Android SDK', 2), ('SD-WAN', 2), ('Azure Storage', 2), ('ReactJS', 2), ('Ember', 2), ('CCNA CCNP', 2), ('JFrog', 2), ('Skype', 2), ('Apache Ignite', 2), ('Apache NiFi', 2), ('Apache Nifi', 2), ('mikrokontrolery', 2), ('Rider', 2), ('Oracle Service Bus', 2), ('Microsoft SQL Server Management Studio', 2), ('Telerik Forms', 2), ('vawr', 2), ('Java J2EE', 2), ('CosmosDB', 2), ('framework Vue', 2), ('TIBCO', 2), ('Tibco', 2), ('Framework Flask', 2), ('Python3', 2), ('RestAssured', 2), ('TS', 2), ('PyLint', 2), ('Azure AWS GCP', 2), ('Yarn', 2), ('Containers Docker', 2), ('RandSQL', 2), ('Assembler', 2), ('Digital Signal Processing', 2), ('Salt', 2), ('RESTful Microservices', 2), ('Vaadin', 2), ('Angular2', 2), ('Pyramid', 2), ('VMs', 2), ('Apache Storm', 2), ('TestComplete', 2), ('Soti', 2), ('Microsoft Active Directory', 2), ('SAP GUI', 2), ('OpenCL', 2), ('CUDA', 2), ('OSCP', 2), ('EPS', 2), ('SAS9', 2), ('CAM', 2), ('GameDev', 2), ('NSA SA', 1), ('SAP S 4 HANA Cloud', 1), ('T SQL', 1), ('MS365', 1), ('pfSense', 1), ('oVirt', 1), ('FreeSwitch', 1), ('Kamailio', 1), ('Asterisk', 1), ('vCenter', 1), ('Elixir', 1), ('Apache ActiveMQ', 1), ('Kubernates', 1), ('OpenVPN', 1), ('OpenLDAP', 1), ('Samba', 1), ('XEN', 1), ('httpd', 1), ('rsync', 1), ('MS SSMS Windows', 1), ('Condluence', 1), ('Azure Cosmos DB', 1), ('Trello', 1), ('Analiza finansowa', 1), ('UML BPMN', 1), ('SAS Guide', 1), ('Jira Atlassian', 1), ('4GL SAS', 1), ('SAS Management Console', 1), ('Jetpack', 1), ('COROUTINES', 1), ('Kubemq', 1), ('Hazelcast', 1), ('JSP Servlets', 1), ('CSF', 1), ('ST', 1), ('Bicep', 1), ('AzureDevOps', 1), ('Elasticache', 1), ('Data Lake Storage', 1), ('DAX Studio', 1), ('Tabular Editor', 1), ('RStudio', 1), ('Talend ETL', 1), ('Tizen', 1), ('Emacs', 1), ('PlayFab', 1), ('Table storage', 1), ('QML', 1), ('Tekton', 1), ('Nutanix', 1), ('GxP', 1), ('Alchemy', 1), ('Microsoft Access Database', 1), ('MS-Office tools', 1), ('Power BI Tableau', 1), ('AWS Redshift', 1), ('Data Management Systems', 1), ('platform DevOps', 1), ('Data enginieering', 1), ('VBA scripting', 1), ('Azure Event Hub', 1), ('Kuberneter', 1), ('Checkmarx', 1), ('Sonar IQ', 1), ('NewSQL', 1), ('Percona Server', 1), ('IIS Web Server', 1), ('Kudu', 1), ('Virtual Machine', 1), ('KeyVault', 1), ('Azure Blueprints', 1), ('HachiCorp Vault', 1), ('AWS Lambda', 1), ('Stepfunction', 1), ('Influx', 1), ('PIWIK Tag Manager', 1), ('Podman', 1), ('Firewall IPS', 1), ('USB', 1), ('GoogleMock', 1), ('Google Test', 1), ('Contiki', 1), ('Ceedling', 1), ('Jaspersoft', 1), ('RedHat OS', 1), ('Polarion', 1), ('Jinja', 1), ('Svelte', 1), ('tcserver', 1), ('React 18', 1), ('DPViewer', 1), ('Stash', 1), ('TypeOrm', 1), ('Prisma', 1), ('Photoshop', 1), ('Babel', 1), ('Adobe Photoshop', 1), ('NetBeans', 1), ('Angular 9', 1), ('Altium Designer', 1), ('PIM PAM', 1), ('AWS Security', 1), ('RSA', 1), ('Pulumi', 1), ('Microsoft Defender', 1), ('PingCastle', 1), ('Print Server', 1), ('Fast API', 1), ('Terraform Terragrunt', 1), ('Project Reactor', 1), ('FFmpeg', 1), ('wyrażenia regularne', 1), ('GPS', 1), ('Azure IOT', 1), ('Espressif ESP', 1), ('AWS IoT Core', 1), ('Zigbee', 1), ('SAP HCM', 1), ('SAP BSP', 1), ('Netflow', 1), ('System Center Operations Manager', 1), ('Basic Data Modelling', 1), ('MS Outlook', 1), ('Jackson', 1), ('Spring Cloud Data Flow', 1), ('JAX-RS', 1), ('Gosu', 1), ('GOSU', 1), ('Spock', 1), ('Angular Material', 1), ('Java11', 1), ('Lombok', 1), ('Protocol Buffers', 1), ('Hyperledger', 1), ('Mule ESB', 1), ('Guidewire', 1), ('AutoML', 1), ('Niemiecki B2', 1), ('Prism Framework', 1), ('Smallworld', 1), ('Silverlight', 1), ('Gulp Webpack', 1), ('PowerAutomate', 1), ('zarządzanie zespołem IT', 1), ('Sigma', 1), ('Six Sigma', 1), ('zdalna obsługa użytkowników', 1), ('Mendix', 1), ('Appian', 1), ('OpenSystems', 1), ('AI RoboticsSQL', 1), ('Informix', 1), ('No-Code', 1), ('SystemVerilog', 1), ('transactSQL', 1), ('Data Integration Studio', 1), ('ATM', 1), ('AQS', 1), ('Theano', 1), ('Contentful', 1), ('Cordova', 1), ('SolarWinds', 1), ('Rundeck', 1), ('Infoblox', 1), ('Solarwinds', 1), ('CCIP', 1), ('Protocol Analyzer', 1), ('Joomla', 1), ('Framework MVC', 1), ('Shopware', 1), ('AEM', 1), ('Icinga', 1), ('ISAE 3402', 1), ('Synology', 1), ('DCS', 1), ('CPQ', 1), ('FCP', 1), ('MS SSIS', 1), ('Linux Embedded', 1), ('REXX', 1), ('DDs', 1), ('Storybook', 1), ('Redux-saga', 1), ('WebStorm', 1), ('Oracle SOA Suite', 1), ('JavaFX', 1), ('MorphX', 1), ('Boostrap', 1), ('MySQL 5', 1), ('PHPStorm', 1), ('MySQL 5 8', 1), ('Memcached', 1), ('ExtJS', 1), ('Oracle GG', 1), ('PHP8', 1), ('Mantis', 1), ('HMI SCADA', 1), ('Couchbase', 1), ('XAML', 1), ('Apache ServiceMix', 1), ('Camel', 1), ('OHS', 1), ('PEP8', 1), ('Asyncio', 1), ('Flask-SQLAlchemy', 1), ('Google Api', 1), ('Twisted', 1), ('unittest', 1), ('Raspberry Pi', 1), ('OAuth2.0', 1), ('ZeroMQ', 1), ('EMV', 1), ('MS Test', 1), ('Kendo UI', 1), ('Sumologic', 1), ('Microcontrollers', 1), ('Transact SQL', 1), ('Matomo', 1), ('Piwik Pro', 1), ('ROS2', 1), ('ROS', 1), ('Terraform Cloud Formation', 1), ('Ansible Chef', 1), ('Blob Storage', 1), ('ADLS', 1), ('Neo4j', 1), ('SAP BAPIs', 1), ('Collaborator', 1), ('event driven architecture', 1), ('Sickit-Learn', 1), ('ARM embedded systems', 1), ('Tensilica HiFi DSP', 1), ('Analog Devices SigmaDSP', 1), ('Java 17', 1), ('Cloudflare', 1), ('Sentry', 1), ('Swing', 1), ('Microsoft Azure Cloud Platform', 1), ('Serverless Framework', 1), ('material UI', 1), ('Exploratory testing', 1), ('Protractor', 1), ('OWASP Top 10', 1), ('WinPhone', 1), ('Apache Hadoop', 1), ('Apache Hive', 1), ('Shopify', 1), ('Backbone.js', 1), ('Gartner', 1), ('Nessus', 1), ('Google Cloud SQL', 1), ('LLVM', 1), ('Gitlab Runners', 1), ('Linux based environment', 1), ('Modern JavaScript', 1), ('VS-Test', 1), ('BrowserStack', 1), ('gimp', 1), ('Inkscape', 1), ('IETF', 1), ('SKD', 1), ('WildFly', 1), ('Temenos T24', 1), ('AnyDesk', 1), ('Windows Mobile', 1), ('OracleSQL', 1), ('ManageEngine', 1), ('Transactional Replication', 1), ('Failover Clustering', 1), ('SQL Server 2008 2019', 1), ('NB-IoT', 1), ('prel', 1), ('diagnozowanie usterek', 1), ('TestFlo', 1), ('IdenityServer', 1), ('KeyCloak', 1), ('Keycloak', 1), ('Resharper', 1), ('Curl', 1), ('Atlassian Stack', 1), ('WorkSpace ONE', 1), ('QMS', 1), ('IM PS', 1), ('SAP MM', 1), ('Next Generation Firewall', 1), ('Serenity', 1), ('Adobe InDesign', 1), ('Load testing', 1), ('TestRail', 1), ('Atomic', 1), ('Vuetify', 1), ('Google Search Console', 1), ('HubSpot', 1)]

Skills_freq_list = []
with open('technologies_trimmed_2.txt', 'r', encoding='utf-8') as file:
    for skill in file:
        skill = skill.replace('\t',',').strip()
        Skills_freq_list.append(tuple(skill.split(',')))

#skill_list = [skill[0] for skill in Skills_freq_list]
#print(skill_list[:500])

'''
with open('technologies_trimmed_2.txt', 'a', encoding='utf-8') as file:
    for skill in Skills_freq_list:
        file.write(f'{skill[0]}\t{skill[1]}\n')
'''

count = 0
for skill in Skills_freq_list:
    #print(skill[0])
    count += int(skill[1])
print(count)

count_decimated = int(count / 10)
print(count_decimated)
skills_90_percent = 9 * count_decimated
skills_80_percent = 8 * count_decimated
skills_70_percent = 7 * count_decimated
skills_60_percent = 6 * count_decimated
skills_50_percent = 5 * count_decimated
print(skills_90_percent,skills_80_percent,skills_70_percent,skills_60_percent,skills_50_percent)

skill_count = 0
count = 0
last_count = 0
for skill in Skills_freq_list:
    skill_count += 1
    count += int(skill[1])
    if count >= skills_90_percent and last_count < skills_90_percent:
        print(f'90% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_80_percent and last_count < skills_80_percent:
        print(f'80% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_70_percent and last_count < skills_70_percent:
        print(f'70% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_60_percent and last_count < skills_60_percent:
        print(f'60% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')
    elif count >= skills_50_percent and last_count < skills_50_percent:
        print(f'50% of skills: {count}  skill names: {skill_count}  last skill: {skill[0]}')

    last_count += int(skill[1])
