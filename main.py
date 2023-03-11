'''
Analyze listings with my skills
'''
import chardet
import json
import re
import datetime


import logging
from logging import config
import logging_functions as l

'''
Result for big batch collected on 10 March 2023:
Regex found 
Pattern Python: 1830 unique matches
Pattern SQL: 3754 unique matches
Pattern \bR\b: 710 unique matches
'''

#Get this script name
log_file_name = __file__.split('\\')
log_file_name = f'{log_file_name[-1][:-3]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file 
l.configure_logging()
logger = logging.getLogger('main')

skills_list = ['Python', 'SQL', 'R']
my_dict = {}

with open('listings_matching_skills.txt', 'r',encoding='UTF-8') as file:
    for line in file:
        #first_line = file.readline()
        my_str = line.strip().replace('•', '')
        my_str = line.replace('\r', '').replace('\n', '').replace('\t', '').replace('\\', '').replace('•', '')
        pattern_offer = r'{\"sectionType\": \"offered\".*?scrollId\": \"offered-1\"}\s*,'
        my_str = re.sub(pattern_offer, '', my_str)
        pattern_clause = r'"informationClause": \{[^}]+\}, '
        my_str = re.sub(pattern_clause, '', my_str)
        pattern_more_quotes = r': \"([^"]*(?:"[^"]*)*)\"'
        #my_str = re.sub(pattern_more_quotes, r': "\1"', my_str)

        # find all matches of pattern in my_str
        matches = re.findall(pattern_more_quotes, my_str)
        if matches:
            print(str(matches)+ '\n'+ '\n'+ '\n')

        #print(json.dumps(my_dict, ensure_ascii=False, indent=4))
        try:
            #Basic listing data
            #url
            my_dict = json.loads(my_str)
            url = my_dict['url']
            job_title = my_dict['offerReducer']['offer']['jobTitle']
            country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
            region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']
            location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']
            salary = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']

            # Assuming both dates always comply to ISO 8601 format, UTC time zone
            publication_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['dateOfInitialPublication']).date()
            expiration_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['expirationDate']).date()

            # technologies
            tech_expected = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][0]['model']['customItems']}
            tech_optional = None
            if len(my_dict['offerReducer']['offer']['sections'][0]['subSections']) > 1:
                tech_optional = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][1]['model']['customItems']}

            # responsibilities
            resp_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][1]['model']['bullets']}

            # requirements
            req_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][0]['model']['bullets']}
            req_optional = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][1]['model']['bullets']}

            # development-practices
            dev_practices = None
            if 'items' in my_dict['offerReducer']['offer']['sections'][4]['model']:
                dev_practices = {practices['code'] for practices in my_dict['offerReducer']['offer']['sections'][4]['model']['items']}
        
        except:
            print(my_str[5400:5500]+ '\n')
            print(my_str+ '\n')
            #print(my_dict['offerReducer']['offer']['sections'][4]['model'])
            l.log_exception('')
            print(json.dumps(my_dict, ensure_ascii=False, indent=4))
            #for i in my_dict['offerReducer']['offer']['sections']:
            #    print(i)
            print('-----------------')
            break


'''
my_str = b'{"url": "https://www.pracuj.pl/praca/pl-sql-developer-szczecin,oferta,1002441655", "toastReducer": {"type": "error", "message": ""}, "applicationReducer": {"application": null, "afterClickLoading": false, "isOneClickApplyActive": false, "applyUrl": "", "multiAts": []}, "employerReducer": {"employer": {"offersLink": ""}, "error": true}, "userReducer": {"email": "", "firstName": "", "lastName": "", "phoneNumber": "", "cvFileName": "", "filestoreId": "", "fileType": ""}, "promptReducer": {"displayed": false, "promptType": "media"}, "offerReducer": {"favourite": false, "revealedPhoneNumber": false, "clauseLongOpened": false, "lifecycle": "", "offer": {"isWholePoland": false, "version": "new-offer", "sections": [{"sectionType": "technologies", "number": 0, "title": "Technologies we use", "header": null, "subSections": [{"sectionType": "technologies-expected", "number": 0, "title": "Expected", "header": null, "subSections": null, "model": {"modelType": "open-dictionary", "dictionaryName": "ItTechnologies", "customItems": [{"name": "PL/SQL"}, {"name": "Oracle"}, {"name": "Java"}, {"name": "Git"}, {"name": "GitLab"}, {"name": "IntelliJ"}, {"name": "SoapUI"}], "items": []}, "id": {"type": "technologies-expected", "number": 1}, "scrollId": "technologies-expected-1"}], "model": {"modelType": ""}, "id": {"type": "technologies", "number": 1}, "scrollId": "technologies-1"}, {"sectionType": "about-project", "number": 0, "title": "About the project", "header": null, "subSections": null, "model": {"modelType": "multi-paragraph", "paragraphs": ["Software Development", "", "Whoever says that software development is a mundane and solitary job has obviously never worked at Sollers. Development is just the beginning of a fascinating journey where we get familiar with business, processes, and architecture. That journey might take you to Barcelona or Tokyo; Paris or Cracow; Cologne or London. The sheer number of projects and customers we have worked with remotely and on-site, guarantees that you will never be bored, you will be on a constant learning curve and get to show off your skills​​.​​"]}, "id": {"type": "about-project", "number": 1}, "scrollId": "about-project-1"}, {"sectionType": "responsibilities", "number": 0, "title": "Your responsibilities", "header": null, "subSections": null, "model": {"modelType": "multi-paragraph", "paragraphs": ["How exactly will you be applying all your skills and talents?", "", "• Implementing, configuring, integrating and customizing software for core insurance systems (TIA, INSIS), according to clients' needs", "• Creating, designing and implementing modern solutions used by our clients (as part of our internal R&D team)"]}, "id": {"type": "responsibilities", "number": 1}, "scrollId": "responsibilities-1"}, {"sectionType": "requirements", "number": 0, "title": "Our requirements", "header": null, "subSections": [{"sectionType": "requirements-expected", "number": 0, "title": "", "header": null, "subSections": null, "model": {"modelType": "multi-paragraph", "paragraphs": ["Speaking of skills, it is quite likely that, at some point, you will be using the following tools and technologies:", "", "• Oracle PL/SQL", "• Oracle ADF", "• Java", "• Git, GitLab/Gerrit, Jenkins and similar", "• PL/SQL Developer, Oracle SQL Developer", "• IntelliJ Idea", "• SoapUI", "• Oracle Database and WebLogic application server", "• ..and more depending on the project", "", "Is it something right up your alley? Let's see if you have what it takes! And what it takes is:", "", "• PL / SQL and Oracle Database basics", "• Any OOP (preferable Java) programming language basics", "• Very good understanding of OOP principles", "• Very good English (min. B2)", "• Good communication skills", "• Understanding of software engineering", "", "You will totally impress us if, on top of the above, you have any of the below:", "", "• Awareness of the software development best practices", "• Willingness to learn new technologies and solutions", "• Teamwork skills and experience", "• Understanding of design patterns", "• Command of French or German", "• Any of the following: Web services (REST / SOAP), Microservices, JMS knowledge, Spring, or any similar hands-on experience"]}, "id": {"type": "requirements-expected", "number": 1}, "scrollId": "requirements-expected-1"}], "model": {"modelType": ""}, "id": {"type": "requirements", "number": 1}, "scrollId": "requirements-1"}, {"sectionType": "work-organization", "number": 0, "title": "This is how we organize our work", "header": null, "subSections": [{"sectionType": "work-organization-work-style", "number": 0, "title": "This is how we work", "header": null, "subSections": null, "model": {"modelType": "open-dictionary", "dictionaryName": "ItWorkStyles", "customItems": [], "items": [{"code": "in-house", "name": "in house", "pracujPlName": "wewnątrz organizacji", "primaryTargetSiteName": "wewnątrz organizacji"}, {"code": "for-client", "name": "at the client's site", "pracujPlName": "u klienta", "primaryTargetSiteName": "u klienta"}, {"code": "one-project", "name": "you focus on a single project at a time", "pracujPlName": "koncentrujesz się na jednym projekcie", "primaryTargetSiteName": "koncentrujesz się na jednym projekcie"}, {"code": "projects-change", "name": "you can change the project", "pracujPlName": "możesz zmienić projekt", "primaryTargetSiteName": "możesz zmienić projekt"}, {"code": "new-project", "name": "you develop the code "from scratch"", "pracujPlName": "tworzysz kod "od zera"", "primaryTargetSiteName": "tworzysz kod "od zera""}, {"code": "product-development", "name": "you focus on product development", "pracujPlName": "koncentrujesz się na rozwoju produktu", "primaryTargetSiteName": "koncentrujesz się na rozwoju produktu"}, {"code": "support", "name": "you focus on code maintenance", "pracujPlName": "koncentrujesz się na utrzymaniu kodu", "primaryTargetSiteName": "koncentrujesz się na utrzymaniu kodu"}, {"code": "agile", "name": "agile", "pracujPlName": "agile", "primaryTargetSiteName": "agile"}, {"code": "scrum", "name": "scrum", "pracujPlName": "scrum", "primaryTargetSiteName": "scrum"}, {"code": "kanban", "name": "kanban", "pracujPlName": "kanban", "primaryTargetSiteName": "kanban"}]}, "id": {"type": "work-organization-work-style", "number": 1}, "scrollId": "work-organization-work-style-1"}, {"sectionType": "work-organization-team-members", "number": 0, "title": "Team members", "header": null, "subSections": null, "model": {"modelType": "open-dictionary", "dictionaryName": "ItTeamMembers", "customItems": [], "items": [{"code": "backend-developer", "name": "backend developer", "pracujPlName": "backend developer", "primaryTargetSiteName": "backend developer"}, {"code": "fullstack-developer", "name": "fullstack developer", "pracujPlName": "fullstack developer", "primaryTargetSiteName": "fullstack developer"}, {"code": "architect", "name": "architect", "pracujPlName": "architekt", "primaryTargetSiteName": "architekt"}, {"code": "devops", "name": "devOps", "pracujPlName": "devOps", "primaryTargetSiteName": "devOps"}, {"code": "project-manager", "name": "project manager", "pracujPlName": "project manager", "primaryTargetSiteName": "project manager"}, {"code": "scrum-master", "name": "scrum master", "pracujPlName": "scrum master", "primaryTargetSiteName": "scrum master"}, {"code": "business-analyst", "name": "business analyst", "pracujPlName": "analityk biznesowy", "primaryTargetSiteName": "analityk biznesowy"}, {"code": "system-analyst", "name": "system analyst", "pracujPlName": "analityk systemowy", "primaryTargetSiteName": "analityk systemowy"}]}, "id": {"type": "work-organization-team-members", "number": 1}, "scrollId": "work-organization-team-members-1"}], "model": {"modelType": ""}, "id": {"type": "work-organization", "number": 1}, "scrollId": "work-organization-1"}, {"sectionType": "development-practices", "number": 0, "title": "This is how we work on a project", "header": null, "subSections": null, "model": {"modelType": "open-dictionary", "dictionaryName": "ItCodingPractices", "customItems": [], "items": [{"code": "code-quality-meters", "name": "code quality measures", "pracujPlName": "mierniki jakości kodu", "primaryTargetSiteName": "mierniki jakości kodu"}, {"code": "code-review", "name": "code review", "pracujPlName": "code review", "primaryTargetSiteName": "code review"}, {"code": "design-patterns", "name": "design patterns", "pracujPlName": "wzorce projektowe", "primaryTargetSiteName": "wzorce projektowe"}, {"code": "static-code-analysis", "name": "static code analysis", "pracujPlName": "statyczna analiza kodu", "primaryTargetSiteName": "statyczna analiza kodu"}, {"code": "tech-lead-support", "name": "architect / technical leader support", "pracujPlName": "wsparcie architekta / lidera technicznego", "primaryTargetSiteName": "wsparcie architekta / lidera technicznego"}, {"code": "continuous-deployment", "name": "Continuous Deployment", "pracujPlName": "Continuous Deployment", "primaryTargetSiteName": "Continuous Deployment"}, {"code": "continuous-integration", "name": "Continuous Integration", "pracujPlName": "Continuous Integration", "primaryTargetSiteName": "Continuous Integration"}, {"code": "dev-ops", "name": "DevOps", "pracujPlName": "DevOps", "primaryTargetSiteName": "DevOps"}, {"code": "documentation", "name": "documentation", "pracujPlName": "dokumentacja", "primaryTargetSiteName": "dokumentacja"}, {"code": "issue-tracking-tools", "name": "issue tracking tools", "pracujPlName": "narzędzia do trackowania zadań", "primaryTargetSiteName": "narzędzia do trackowania zadań"}, {"code": "tech-debt-management", "name": "technical debt management", "pracujPlName": "zarządzanie długiem technologicznym", "primaryTargetSiteName": "zarządzanie długiem technologicznym"}, {"code": "functional-tests", "name": "functional tests", "pracujPlName": "testy funkcjonalne", "primaryTargetSiteName": "testy funkcjonalne"}, {"code": "integration-tests", "name": "integration tests", "pracujPlName": "testy integracyjne", "primaryTargetSiteName": "testy integracyjne"}, {"code": "performance-tests", "name": "performance tests", "pracujPlName": "testy wydajnościowe", "primaryTargetSiteName": "testy wydajnościowe"}, {"code": "regression-tests", "name": "regression tests", "pracujPlName": "testy regresyjne", "primaryTargetSiteName": "testy regresyjne"}, {"code": "tests-automation", "name": "test automation", "pracujPlName": "automatyzacja testów", "primaryTargetSiteName": "automatyzacja testów"}, {"code": "tests-environments", "name": "testing environments", "pracujPlName": "środowiska testowe", "primaryTargetSiteName": "środowiska testowe"}, {"code": "unit-tests", "name": "unit tests", "pracujPlName": "testy jednostkowe", "primaryTargetSiteName": "testy jednostkowe"}]}, "id": {"type": "development-practices", "number": 1}, "scrollId": "development-practices-1"}, {"sectionType": "training-space", "number": 0, "title": "Development opportunities we offer", "header": null, "subSections": null, "model": {"modelType": "open-dictionary", "dictionaryName": "ItPersonalGrowthOpportunities", "customItems": [], "items": [{"code": "foreign-conferences", "name": "conferences abroad", "pracujPlName": "konferencje zagraniczne", "primaryTargetSiteName": "konferencje zagraniczne"}, {"code": "conferences-in-poland", "name": "conferences in Poland", "pracujPlName": "konferencje w Polsce", "primaryTargetSiteName": "konferencje w Polsce"}, {"code": "development-budget", "name": "development budget", "pracujPlName": "budżet rozwojowy", "primaryTargetSiteName": "budżet rozwojowy"}, {"code": "external-trainings", "name": "external training", "pracujPlName": "szkolenia zewnętrzne", "primaryTargetSiteName": "szkolenia zewnętrzne"}, {"code": "in-company-trainings", "name": "intracompany training", "pracujPlName": "szkolenia wewnątrzfirmowe", "primaryTargetSiteName": "szkolenia wewnątrzfirmowe"}, {"code": "mentoring", "name": "mentoring", "pracujPlName": "mentoring", "primaryTargetSiteName": "mentoring"}, {"code": "soft-skills-trainings", "name": "soft skills training", "pracujPlName": "treningi umiejętności miękkich", "primaryTargetSiteName": "treningi umiejętności miękkich"}, {"code": "technical-leader-support", "name": "substantive support from technological leaders", "pracujPlName": "wsparcie merytoryczne od liderów technologicznych", "primaryTargetSiteName": "wsparcie merytoryczne od liderów technologicznych"}]}, "id": {"type": "training-space", "number": 1}, "scrollId": "training-space-1"},  {"sectionType": "benefits", "number": 0, "title": "Benefits", "header": null, "subSections": null, "model": {"modelType": "open-dictionary-with-icons", "dictionaryName": "Benefits", "customItems": [{"name": "employee assistance program", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/custom.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/custom.svg"}}], "items": [{"code": "medical-care", "name": "private medical care", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/medical-care.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/medical-care.svg"}}, {"code": "lang-learning", "name": "sharing the costs of foreign language classes", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/lang-learning.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/lang-learning.svg"}}, {"code": "co-fin-train-courses", "name": "sharing the costs of professional training & courses", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/co-fin-train-courses.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/co-fin-train-courses.svg"}}, {"code": "life-insurance", "name": "life insurance", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/life-insurance.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/life-insurance.svg"}}, {"code": "remote-work", "name": "remote work opportunities", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/remote-work.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/remote-work.svg"}}, {"code": "flex-work-time", "name": "flexible working time", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/flex-work-time.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/flex-work-time.svg"}}, {"code": "integration-meetings", "name": "integration events", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/integration-meetings.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/integration-meetings.svg"}}, {"code": "dental-care", "name": "dental care", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/dental-care.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/dental-care.svg"}}, {"code": "private-computer", "name": "computer available for private use", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/private-computer.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/private-computer.svg"}}, {"code": "company-library", "name": "corporate library", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/company-library.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/company-library.svg"}}, {"code": "video-games", "name": "video games at work", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/video-games.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/video-games.svg"}}, {"code": "relaxation-zone", "name": "leisure zone", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/relaxation-zone.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/relaxation-zone.svg"}}, {"code": "relocation-package", "name": "redeployment package", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/relocation-package.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/relocation-package.svg"}}, {"code": "recommendation-program", "name": "employee referral program", "icon": {"rasterUrl": "https://skidblandir.gpcdn.pl/icons/benefits/recommendation-program.png", "vectorUrl": "https://skidblandir.gpcdn.pl/icons/benefits/recommendation-program.svg"}}]}, "id": {"type": "benefits", "number": 1}, "scrollId": "benefits-1"}, {"sectionType": "recruitment-stages", "number": 0, "title": "Recruitment stages", "header": null, "subSections": null, "model": {"modelType": "bullets", "bullets": ["CV evaluation", "Homework/Phone interview", "Interview (MS Teams)"]}, "id": {"type": "recruitment-stages", "number": 1}, "scrollId": "recruitment-stages-1"}, {"sectionType": "about-us-extended", "number": 0, "title": "", "header": null, "subSections": [{"sectionType": "about-us-description", "number": 0, "title": "Sollers Consulting", "header": null, "subSections": null, "model": {"modelType": "multi-paragraph", "paragraphs": ["We are a Team of over 900 professionals who build the Digital Future for the world’s largest insurance, banking and leasing organisations. Our history of business advisory and software implementation goes back to the year 2000. Sollers Consulting’s roots are in Europe, but the company’s footprint is visible around the world.", "", "As an international company with offices & projects around the world and Sollers of 20+ nationalities, we thrive in our multi-culture. We guarantee you will feel like you belong here, whether you are from Poland, the West, the East or another hemisphere."]}, "id": {"type": "about-us-description", "number": 1}, "scrollId": "about-us-description-1"}, {"sectionType": "about-us-gallery", "number": 0, "title": "This is how we work", "header": null, "subSections": null, "model": {"modelType": "gallery", "items": [{"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/2c580000-43a8-f403-97ce-08d99862c227.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/2c580000-43a8-f403-97ce-08d99862c227.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/ee4d0000-5df0-0015-0ec1-08daf54cd34a.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/ee4d0000-5df0-0015-0ec1-08daf54cd34a.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/2c580000-43a8-f403-42d5-08d98e3e654a.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/2c580000-43a8-f403-42d5-08d98e3e654a.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-1edf-08daf54d3979.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-1edf-08daf54d3979.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-a442-08daf54dbea5.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-a442-08daf54dbea5.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/ee4d0000-5df0-0015-7429-08daf54de3f4.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/ee4d0000-5df0-0015-7429-08daf54de3f4.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-abf5-08daf54d9c42.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-abf5-08daf54d9c42.jpg", "grubberId": null}, {"mediaType": "picture", "url": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-79ce-08daf54d7736.jpg", "thumbnailUrl": "https://grubber.gpcdn.pl/companies/15058520/gallery-images/9b030000-5dac-0015-79ce-08daf54d7736.jpg", "grubberId": null}]}, "id": {"type": "about-us-gallery", "number": 1}, "scrollId": "about-us-gallery-1"}], "model": {"modelType": ""}, "id": {"type": "about-us-extended", "number": 1}, "scrollId": "about-us-extended-1"}], "primaryAttributes": [{"code": "many-vacancies", "label": {"text": "More than one vacancy", "pracujPlText": "Szukamy wielu kandydatów", "primaryTargetSiteText": "Szukamy wielu kandydatów"}, "model": {"modelType": "flag-with-number", "flag": true, "number": null}}], "secondaryAttributes": [], "employerName": "Sollers Consulting", "jobOfferLanguage": {"isoCode": "en"}, "jobTitle": "PL/SQL Developer", "workplaces": [{"abroadAddress": null, "isAbroad": false, "country": {"id": 1, "name": "Poland", "pracujPlName": "Polska"}, "region": {"id": 16, "name": "West Pomeranian", "pracujPlName": "zachodniopomorskie"}, "inlandLocation": {"location": {"id": 668, "name": "Szczecin"}, "address": null}, "displayAddress": "Szczecin"}], "remoteWork": false, "requireCV": true, "typesOfContracts": [{"id": 0, "name": "contract of employment", "pracujPlName": "umowa o pracę", "salary": null}, {"id": 3, "name": "B2B contract", "pracujPlName": "kontrakt B2B", "salary": null}], "workSchedules": "full-time", "positionLevelsName": "specialist (Mid / Regular)", "workModes": [{"text": "hybrid work", "subText": ""}], "offerRelativeUri": "pl-sql-developer-szczecin,oferta,1002441655", "dateOfInitialPublication": "2023-03-06T08:14:08.98Z", "expirationDate": "2023-04-03T21:59:59Z", "offerURLName": "pl-sql-developer-szczecin,oferta,1002441655", "terminated": false, "offerId": 1002441655, "commonOfferId": null, "referenceNumber": "", "companyId": 15058520, "categories": [{"id": 5015001, "name": "Administrowanie bazami danych i storage", "parent": {"id": 5015, "name": "IT - Administracja"}}, {"id": 5016002, "name": "Architektura", "parent": {"id": 5016, "name": "IT - Rozwój oprogramowania"}}, {"id": 5016003, "name": "Programowanie", "parent": {"id": 5016, "name": "IT - Rozwój oprogramowania"}}], "oneClickApply": false, "applying": {"applyingType": "ats", "applyingModel": {"optionalCv": false, "formUrl": "https://sollers.eu/careers/plsql-developer/?utm_source=JobBoards&utm_medium=IT_pracuj&utm_campaign=PLSQL_Developer", "formMode": "single", "multiApplying": []}}, "applyTypeId": 0, "appType": 0, "applyLink": "https://www.pracuj.pl/aplikuj/pl-sql-developer-szczecin,oferta,1002441655", "countryId": 1, "countryName": "Poland", "regionId": 16, "regionName": "West Pomeranian", "locationName": "Szczecin", "phone": null, "isRemoteRecruitment": true, "isMultiAts": false, "multiAtsLocations": [], "textTemplate": null, "template": null, "clause": null, "style": {"themeColor": {"hex": "#1825aa"}, "fontColor": {"hex": "#ffffff"}, "logo": "https://logos.gpcdn.pl/loga-firm/15058520/03000000-bb2f-3863-e31e-08d9b4d01926_280x280.jpg", "images": ["https://grubber.gpcdn.pl/companies/15058520/background-images/03000000-bb2f-3863-69aa-08d99ea8ab09.png"], "sectionsBackground": ""}, "hasClauseInfo": false, "jobiconCompanyInfo": ""}}, "credentialsReducer": {"mpUserId": 0, "identityId": ""}, "breadcrumbsReducer": {"breadcrumbs": [{"label": "Praca", "absoluteUrl": "https://www.pracuj.pl/praca", "children": null}, {"label": "Szczecin", "absoluteUrl": "https://www.pracuj.pl/praca/szczecin;wp", "children": [{"label": "Koszalin", "absoluteUrl": "https://www.pracuj.pl/praca/koszalin;wp"}, {"label": "Stargard", "absoluteUrl": "https://www.pracuj.pl/praca/stargard;wp"}, {"label": "Warszawa", "absoluteUrl": "https://www.pracuj.pl/praca/warszawa;wp"}, {"label": "Kraków", "absoluteUrl": "https://www.pracuj.pl/praca/krakow;wp"}, {"label": "Łódź", "absoluteUrl": "https://www.pracuj.pl/praca/lodz;wp"}]}, {"label": "IT - Administracja", "absoluteUrl": "https://www.pracuj.pl/praca/it%20-%20administracja;cc,5015", "children": [{"label": "IT - Rozwój oprogramowania", "absoluteUrl": "https://www.pracuj.pl/praca/it%20-%20rozw%c3%b3j%20oprogramowania;cc,5016"}]}, {"label": "Administrowanie bazami danych i storage", "absoluteUrl": "https://www.pracuj.pl/praca/it%20-%20administracja;cc,5015/administrowanie%20bazami%20danych%20i%20storage;cc,5015001", "children": [{"label": "Architektura", "absoluteUrl": "https://www.pracuj.pl/praca/it%20-%20rozw%c3%b3j%20oprogramowania;cc,5016/architektura;cc,5016002"}, {"label": "Programowanie", "absoluteUrl": "https://www.pracuj.pl/praca/it%20-%20rozw%c3%b3j%20oprogramowania;cc,5016/programowanie;cc,5016003"}]}]}}'.decode('utf-8', 'ignore')
print(my_str)
my_str = my_str.replace('\r', '').replace('\n', '').replace('\t', '').replace('\\', '').replace('•', '')
pattern_more_quotes = r'"([^"]*)"[^"]*"'
my_str = re.sub(pattern_more_quotes, r'"\1"', my_str)
#print(my_str[5400:5500])

my_dict = json.loads(my_str)
#print(json.dumps(my_dict, ensure_ascii=False, indent=4))


'''
'''
'''
'''
# Detect the encoding of the string
detected_encoding = chardet.detect(my_str.encode())['encoding']

# Decode the string using the detected encoding
my_str_decoded = my_str.encode(detected_encoding).decode()

# Load the JSON string into a dictionary
my_dict = json.loads(my_str_decoded)

# Print the dictionary
print(json.dumps(my_dict, ensure_ascii=False, indent=4))
'''

'''
my_str_encoded = my_str.encode('iso-8859-1', errors='replace')
my_dict = json.loads(my_str_encoded.decode('utf-8'))
print(json.dumps(my_dict, ensure_ascii=False, indent=4))
'''
'''
encodings = ['UTF-8', 'ISO-8859-1', 'UTF-16', 'UTF-32']

for encoding in encodings:
    try:
        my_dict = json.loads(my_str.encode(encoding).decode('utf-8'))
        print(my_dict)
    except Exception as e:
        print(f"Error with {encoding}: {e}")

'''


'''

#Basic listing data
#url
url = my_dict['url']
job_title = my_dict['offerReducer']['offer']['jobTitle']
country = my_dict['offerReducer']['offer']['workplaces'][0]['country']['name']
region = my_dict['offerReducer']['offer']['workplaces'][0]['region']['name']
location = my_dict['offerReducer']['offer']['workplaces'][0]['inlandLocation']['location']['name']
salary = my_dict['offerReducer']['offer']['typesOfContracts'][0]['salary']

# Assuming both dates always comply to ISO 8601 format, UTC time zone
publication_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['dateOfInitialPublication']).date()
expiration_date = datetime.datetime.fromisoformat(my_dict['offerReducer']['offer']['expirationDate']).date()

# technologies
tech_expected = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][0]['model']['customItems']}
tech_optional = {tech['name'] for tech in my_dict['offerReducer']['offer']['sections'][0]['subSections'][1]['model']['customItems']}

# responsibilities
resp_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][1]['model']['bullets']}

# requirements
req_expected = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][0]['model']['bullets']}
req_optional = {resp for resp in my_dict['offerReducer']['offer']['sections'][2]['subSections'][1]['model']['bullets']}

# development-practices
dev_practices = {practices['code'] for practices in my_dict['offerReducer']['offer']['sections'][4]['model']['items']}


'''



































'''
for i in dev_practices:
    print(i)
'''

'''

#def extract_usefull_listings(skills_list):
Extract listings that have my skills
    # Patterns for skills_slist = ['Python', 'SQL', 'R']
    # Designed to find SQL
    pattern_1 = r'%s'
    # Designed to find R language
    pattern_2 = r'\b%s\b'

    patterns_list = [pattern_1 % skills_list[0], pattern_1 % skills_list[1],
    pattern_2 % skills_list[2]]

    with open('listings_json_data.txt', 'r',encoding='UTF-8') as input_file, \
    open('listings_matching_skills.txt', 'a',encoding='UTF-8') as output_file:
        #Find all JSON that contain my skills
        matches = set()
        for pattern in patterns_list:
            # Set comprehensioin to filter out listings with my skills
            new_matches = {line for line in input_file if re.search(pattern, line)}
            
            # Merge the sets of matches
            matches |= new_matches

            # Reset the input file pointer to the beginning
            input_file.seek(0)

            # Print the number of unique matches for this pattern
            print(f"Pattern {pattern}: {len(new_matches)} unique matches")
        # Write the matching lines to the output file
        for match in matches:
            output_file.write(match)
'''